"""Convert ATS-specific records into the project's common schema."""

from __future__ import annotations

from datetime import datetime, timezone
import html
import re
from typing import Any

from .config import Source, is_in_role, is_us_location


CANONICAL_COLUMNS = (
    "posting_key",
    "employer",
    "source",
    "source_id",
    "title",
    "location",
    "team",
    "employment_type",
    "workplace_type",
    "salary_min",
    "salary_max",
    "salary_currency",
    "salary_text",
    "salary_period",
    "salary_annual_min",
    "salary_annual_max",
    "description_excerpt",
    "description",
    "apply_url",
    "posted_at",
    "first_seen",
    "last_seen",
    "removed_date",
    "in_role",
    "is_us",
    "is_internship",
    "is_new_grad",
    "sponsorship",
    "degree_requirement",
    "program_type",
    "duplicate_key",
    "first_run",
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(_text(item) for item in value if _text(item))
    if isinstance(value, dict):
        for key in ("name", "label", "text", "title", "location", "display_name"):
            if value.get(key):
                return _text(value[key])
        return ""
    return str(value).strip()


def strip_html(value: Any) -> str:
    """Make source HTML readable without adding an HTML parser dependency."""

    text = html.unescape(_text(value))
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[ \t]+", " ", text).strip()


def _date_or_empty(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)):
        # Lever returns milliseconds since epoch.
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()
    return str(value).strip()


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"\d[\d,]*(?:\.\d+)?", str(value))
    if not match:
        return None
    return float(match.group(0).replace(",", ""))


def _salary(raw: dict[str, Any], ats: str) -> tuple[float | None, float | None, str, str]:
    minimum: float | None = None
    maximum: float | None = None
    currency = ""
    text = ""

    if ats == "greenhouse":
        ranges = raw.get("pay_input_ranges") or []
        if ranges:
            band = ranges[0] if isinstance(ranges[0], dict) else {}
            minimum = _number(band.get("min_cents"))
            maximum = _number(band.get("max_cents"))
            if minimum is not None:
                minimum /= 100
            if maximum is not None:
                maximum /= 100
            currency = _text(band.get("currency"))
            text = _text(band.get("interval"))
    elif ats == "adzuna":
        minimum = _number(raw.get("salary_min"))
        maximum = _number(raw.get("salary_max"))
        currency = _text(raw.get("salary_currency"))
    elif ats == "usajobs":
        bands = raw.get("PositionRemuneration") or []
        if bands and isinstance(bands[0], dict):
            band = bands[0]
            minimum = _number(band.get("MinimumRange"))
            maximum = _number(band.get("MaximumRange"))
            currency = _text(band.get("CurrencyCode")) or "USD"
            text = _text(band.get("RateIntervalCode"))
    elif ats in {"jibe", "phenom"}:
        minimum = _number(raw.get("salary_min_value") or raw.get("salary_min"))
        maximum = _number(raw.get("salary_max_value") or raw.get("salary_max"))
        currency = _text(raw.get("salary_currency"))
        text = _text(raw.get("salary"))
    else:
        value = raw.get("salary") or raw.get("salary_text") or raw.get("compensation")
        if isinstance(value, dict):
            minimum = _number(value.get("min") or value.get("minimum") or value.get("minValue"))
            maximum = _number(value.get("max") or value.get("maximum") or value.get("maxValue"))
            currency = _text(value.get("currency") or value.get("currencyCode"))
            text = _text(value.get("text"))
        else:
            text = _text(value)
            numbers = re.findall(r"\$?\s*\d[\d,]*(?:\.\d+)?", text)
            if numbers:
                minimum = _number(numbers[0])
                maximum = _number(numbers[-1])

    # Some feeds expose the salary object without using the adapter's usual
    # field names. Keep the signal instead of dropping it as an unknown field.
    if minimum is None and maximum is None and not text:
        value = raw.get("salary") or raw.get("salary_text") or raw.get("compensation")
        if isinstance(value, dict):
            minimum = _number(value.get("min") or value.get("minimum") or value.get("minValue"))
            maximum = _number(value.get("max") or value.get("maximum") or value.get("maxValue"))
            currency = _text(value.get("currency") or value.get("currencyCode"))
            text = _text(value.get("text"))
        else:
            text = _text(value)
            numbers = re.findall(r"\$?\s*\d[\d,]*(?:\.\d+)?", text)
            if numbers:
                minimum = _number(numbers[0])
                maximum = _number(numbers[-1])

    if not currency and (minimum is not None or maximum is not None or "$" in text):
        currency = "USD"
    if text and re.fullmatch(r"\s*\d[\d,]*(?:\.\d+)?\s*(?:[A-Za-z]+)?\s*", text):
        low = f"${minimum:,.0f}" if minimum is not None else ""
        high = f"${maximum:,.0f}" if maximum is not None else ""
        text = f"{low}–{high}" if low and high and low != high else (low or high)
    if not text and (minimum is not None or maximum is not None):
        low = f"${minimum:,.0f}" if minimum is not None else ""
        high = f"${maximum:,.0f}" if maximum is not None else ""
        text = f"{low}–{high}" if low and high and low != high else (low or high)
    return minimum, maximum, currency, text


def _salary_period(text: str, minimum: float | None, maximum: float | None) -> str:
    value = text.lower()
    if re.search(r"\b(?:hour|hourly)\b", value):
        return "hour"
    if re.search(r"\b(?:week|weekly)\b", value):
        return "week"
    if re.search(r"\b(?:month|monthly)\b", value):
        return "month"
    if re.search(r"\b(?:year|annual|annually|salary)\b", value):
        return "year"
    # Employer salary bands without an interval are normally annual ranges.
    return "year" if minimum is not None or maximum is not None else "unknown"


def _annualize(value: float | None, period: str) -> float | None:
    if value is None:
        return None
    return value * {"hour": 2080, "week": 52, "month": 12, "year": 1}.get(period, 1)


def _signals(title: str, description: str, workplace_type: str) -> tuple[bool, bool, str, str]:
    text = f"{title} {description}".lower()
    internship = bool(re.search(r"\b(?:intern(?:ship)?|summer analyst|campus program)\b", text))
    new_grad = bool(re.search(r"\b(?:new grad(?:uate)?|early career|recent graduate|students?\s*&?\s*grads?|rotational|campus|university|analyst program)\b|\b20(?:2[6-9]|3\d)\b", text))
    if re.search(r"(?:will not|does not|no)\s+(?:provide\s+)?(?:visa|employment|immigration)?\s*sponsorship|without sponsorship|not sponsor", text):
        sponsorship = "no"
    elif re.search(r"sponsor(?:ship)?|visa|work authorization|immigration", text):
        sponsorship = "mentioned"
    else:
        sponsorship = "unknown"
    if re.search(r"\b(?:bachelor(?:'s)?|master(?:'s)?|doctoral|phd|degree required|college degree)\b", text):
        degree = "mentioned"
    else:
        degree = "not-listed"
    return internship, new_grad, sponsorship, degree


def _program_type(title: str, description: str, is_internship: bool, is_new_grad: bool) -> str:
    text = f"{title} {description}".lower()
    if is_internship:
        return "Internship / campus"
    if re.search(r"\b(?:rotational|rotation|development program|leadership program)\b", text):
        return "Rotational / leadership"
    if re.search(r"\b(?:analyst program|new grad(?:uate)?|early career|campus|university)\b", text) or is_new_grad:
        return "New graduate program"
    return "Entry-level"


def _duplicate_key(employer: str, title: str, location: str) -> str:
    value = " ".join((employer, title, location)).lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def _location(source: Source, raw: dict[str, Any]) -> str:
    ats = source.ats.lower()
    if ats == "greenhouse":
        location = raw.get("location")
        if isinstance(location, dict):
            return _text(location.get("name"))
        return _text(location)
    if ats == "lever":
        categories = raw.get("categories") or {}
        return _text(categories.get("location") or raw.get("location"))
    if ats == "adzuna":
        return _text(raw.get("location"))
    if ats == "jooble":
        return _text(raw.get("location"))
    if ats == "usajobs":
        return _text(raw.get("PositionLocationDisplay") or raw.get("PositionLocation"))
    if ats == "workday":
        return _text(raw.get("locationsText") or raw.get("location"))
    if ats == "oracle":
        return _text(raw.get("PrimaryLocation") or raw.get("location"))
    if ats == "phenom":
        if raw.get("country") or raw.get("state") or raw.get("city"):
            parts = [raw.get("city"), raw.get("state"), raw.get("country")]
            return ", ".join(_text(part) for part in parts if _text(part))
        return _text(raw.get("location") or raw.get("cityStateCountry") or raw.get("locationLatlong"))
    if ats == "eightfold":
        return _text(raw.get("locations") or raw.get("location"))
    if ats == "jibe":
        return _text(raw.get("location") or raw.get("full_location"))
    if ats == "mcloud":
        parts = [raw.get("primary_city"), raw.get("primary_state"), raw.get("primary_country")]
        return ", ".join(_text(part) for part in parts if _text(part))
    location = raw.get("location")
    if isinstance(location, list):
        return ", ".join(_text(item) for item in location)
    return _text(location)


def _team(source: Source, raw: dict[str, Any]) -> str:
    ats = source.ats.lower()
    if ats == "greenhouse":
        departments = raw.get("departments") or []
        return ", ".join(_text(item.get("name") if isinstance(item, dict) else item) for item in departments)
    if ats == "lever":
        categories = raw.get("categories") or {}
        return _text(categories.get("team") or categories.get("department"))
    if ats == "adzuna":
        return _text((raw.get("category") or {}).get("label"))
    if ats == "usajobs":
        return _text(raw.get("JobCategory") or raw.get("JobCategoryName"))
    if ats == "workday":
        return _text(raw.get("bulletFields") or raw.get("jobFamily") or raw.get("jobFunction"))
    if ats == "oracle":
        return _text(raw.get("JobFamily") or raw.get("JobFunction") or raw.get("Department"))
    if ats == "phenom":
        categories = raw.get("multi_category") or raw.get("category")
        return _text(categories)
    if ats == "eightfold":
        return _text(raw.get("department"))
    if ats == "jibe":
        return _text(raw.get("department") or raw.get("category"))
    if ats == "mcloud":
        return _text(raw.get("function") or raw.get("primary_category"))
    return _text(raw.get("department") or raw.get("team"))


def normalize_posting(raw: dict[str, Any], source: Source) -> dict[str, Any]:
    """Return one canonical posting row for the supported public ATS feeds."""

    ats = source.ats.lower()
    source_id = _text(
        raw.get("_source_id")
        or raw.get("id")
        or raw.get("Id")
        or raw.get("jobId")
        or raw.get("job_id")
        or raw.get("PositionID")
        or raw.get("req_id")
        or raw.get("reqId")
        or raw.get("jobSeqNo")
        or (raw.get("bulletFields") or [None])[0]
        or raw.get("externalPath")
    )
    title = _text(raw.get("title") or raw.get("text") or raw.get("name") or raw.get("PositionTitle") or raw.get("Title"))
    employer = source.employer
    if ats in {"adzuna", "jooble"}:
        employer = _text(raw.get("company")) or source.employer
    elif ats == "usajobs":
        employer = _text(raw.get("OrganizationName")) or source.employer

    if ats == "greenhouse":
        apply_url = _text(raw.get("absolute_url") or raw.get("url"))
        description = strip_html(raw.get("content"))
        employment_type = _text(raw.get("metadata"))
        workplace_type = ""
        posted_at = _date_or_empty(raw.get("updated_at"))
    elif ats == "lever":
        apply_url = _text(raw.get("applyUrl") or raw.get("hostedUrl") or raw.get("url"))
        description = strip_html(raw.get("descriptionPlain") or raw.get("description"))
        categories = raw.get("categories") or {}
        employment_type = _text(categories.get("commitment") or raw.get("employmentType"))
        workplace_type = _text(categories.get("workplaceType") or raw.get("workplaceType"))
        posted_at = _date_or_empty(raw.get("createdAt"))
    elif ats == "adzuna":
        apply_url = _text(raw.get("redirect_url") or raw.get("url"))
        description = strip_html(raw.get("description"))
        employment_type = _text(raw.get("contract_type") or raw.get("contract_time"))
        workplace_type = "Remote" if "remote" in f"{title} {_location(source, raw)}".lower() else ""
        posted_at = _date_or_empty(raw.get("created"))
    elif ats == "jooble":
        apply_url = _text(raw.get("link") or raw.get("url"))
        description = strip_html(raw.get("snippet") or raw.get("description"))
        employment_type = _text(raw.get("type"))
        workplace_type = "Remote" if "remote" in f"{title} {_location(source, raw)}".lower() else ""
        posted_at = _date_or_empty(raw.get("updated"))
    elif ats == "usajobs":
        apply_url = _text(raw.get("PositionURI") or raw.get("ApplyURI") or raw.get("url"))
        description = strip_html(raw.get("UserArea", {}).get("Details", {}).get("JobSummary") or raw.get("QualificationSummary"))
        employment_type = _text(raw.get("PositionSchedule"))
        workplace_type = "Remote" if "remote" in f"{title} {_location(source, raw)}".lower() else ""
        posted_at = _date_or_empty(raw.get("PublicationStartDate"))
    elif ats == "workday":
        apply_url = _text(raw.get("_apply_url") or raw.get("url"))
        description = strip_html(raw.get("description"))
        employment_type = _text(raw.get("timeType"))
        workplace_type = _text(raw.get("remoteType"))
        posted_at = _date_or_empty(raw.get("postedOn"))
    elif ats == "oracle":
        apply_url = _text(raw.get("_apply_url") or raw.get("url"))
        description = strip_html(
            raw.get("ShortDescriptionStr")
            or raw.get("ExternalQualificationsStr")
            or raw.get("ExternalResponsibilitiesStr")
        )
        employment_type = _text(raw.get("WorkerType") or raw.get("JobType") or raw.get("JobSchedule"))
        workplace_type = _text(raw.get("WorkplaceType") or raw.get("WorkplaceTypeCode"))
        posted_at = _date_or_empty(raw.get("PostedDate"))
    elif ats == "phenom":
        apply_url = _text(raw.get("applyUrl") or raw.get("url"))
        description = strip_html(raw.get("description") or raw.get("descriptionTeaser") or (raw.get("ml_job_parser") or {}).get("descriptionTeaser_ats"))
        employment_type = _text(raw.get("type"))
        workplace_type = _text(raw.get("workLocationOption"))
        posted_at = _date_or_empty(raw.get("postedDate"))
    elif ats == "eightfold":
        apply_url = _text(raw.get("_apply_url") or raw.get("positionUrl") or raw.get("url"))
        description = strip_html(raw.get("description"))
        employment_type = _text(raw.get("employmentType"))
        workplace_type = _text(raw.get("workLocationOption"))
        posted_value = raw.get("posted_at") or raw.get("postedTs")
        if isinstance(posted_value, (int, float)):
            posted_at = datetime.fromtimestamp(posted_value, tz=timezone.utc).isoformat()
        else:
            posted_at = _date_or_empty(posted_value)
    elif ats == "jibe":
        apply_url = _text(raw.get("apply_url") or raw.get("url"))
        description = strip_html(raw.get("description") or raw.get("qualifications") or raw.get("responsibilities"))
        employment_type = _text(raw.get("employment_type"))
        workplace_type = _text(raw.get("location_type"))
        posted_at = _date_or_empty(raw.get("posted_date") or raw.get("create_date"))
    elif ats == "mcloud":
        apply_url = _text(raw.get("url") or raw.get("seo_url") or raw.get("fndly_url"))
        description = strip_html(raw.get("description"))
        employment_type = _text(raw.get("employment_type") or raw.get("job_type"))
        workplace_type = _text(raw.get("location_type"))
        posted_at = _date_or_empty(raw.get("open_date") or raw.get("update_date"))
    else:
        apply_url = _text(raw.get("jobUrl") or raw.get("applyUrl") or raw.get("url"))
        description = strip_html(raw.get("descriptionHtml") or raw.get("description"))
        employment_type = _text(raw.get("employmentType"))
        workplace_type = _text(raw.get("workplaceType"))
        posted_at = _date_or_empty(raw.get("publishedAt"))

    location = _location(source, raw)
    if not workplace_type:
        workplace_match = re.search(r"\b(remote|hybrid|on[- ]?site)\b", f"{title} {location} {description}", re.IGNORECASE)
        workplace_type = workplace_match.group(1).title() if workplace_match else ""
    salary_min, salary_max, salary_currency, salary_text = _salary(raw, ats)
    salary_period = _salary_period(salary_text, salary_min, salary_max)
    salary_annual_min = _annualize(salary_min, salary_period)
    salary_annual_max = _annualize(salary_max, salary_period)
    is_internship, is_new_grad, sponsorship, degree_requirement = _signals(title, description, workplace_type)
    program_type = _program_type(title, description, is_internship, is_new_grad)
    return {
        "posting_key": f"{source.id}:{source_id}",
        "employer": employer,
        "source": source.id,
        "source_id": source_id,
        "title": title,
        "location": location,
        "team": _team(source, raw),
        "employment_type": employment_type,
        "workplace_type": workplace_type,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary_currency,
        "salary_text": salary_text,
        "salary_period": salary_period,
        "salary_annual_min": salary_annual_min,
        "salary_annual_max": salary_annual_max,
        "description_excerpt": description[:450],
        "description": description,
        "apply_url": apply_url,
        "posted_at": posted_at,
        "first_seen": "",
        "last_seen": "",
        "removed_date": "",
        "in_role": is_us_location(location) and is_in_role(title, description),
        "is_us": is_us_location(location),
        "is_internship": is_internship,
        "is_new_grad": is_new_grad,
        "sponsorship": sponsorship,
        "degree_requirement": degree_requirement,
        "program_type": program_type,
        "duplicate_key": _duplicate_key(employer, title, location),
        "first_run": False,
    }

