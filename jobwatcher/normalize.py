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
    "description",
    "apply_url",
    "posted_at",
    "first_seen",
    "last_seen",
    "removed_date",
    "in_role",
    "is_us",
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


def _location(source: Source, raw: dict[str, Any]) -> str:
    if source.ats.lower() == "greenhouse":
        location = raw.get("location")
        if isinstance(location, dict):
            return _text(location.get("name"))
        return _text(location)
    if source.ats.lower() == "lever":
        categories = raw.get("categories") or {}
        return _text(categories.get("location") or raw.get("location"))
    if source.ats.lower() == "adzuna":
        return _text(raw.get("location"))
    if source.ats.lower() == "jooble":
        return _text(raw.get("location"))
    if source.ats.lower() == "usajobs":
        return _text(raw.get("PositionLocationDisplay") or raw.get("PositionLocation"))
    location = raw.get("location")
    if isinstance(location, list):
        return ", ".join(_text(item) for item in location)
    return _text(location)


def _team(source: Source, raw: dict[str, Any]) -> str:
    if source.ats.lower() == "greenhouse":
        departments = raw.get("departments") or []
        return ", ".join(_text(item.get("name") if isinstance(item, dict) else item) for item in departments)
    if source.ats.lower() == "lever":
        categories = raw.get("categories") or {}
        return _text(categories.get("team") or categories.get("department"))
    if source.ats.lower() == "adzuna":
        return _text((raw.get("category") or {}).get("label"))
    if source.ats.lower() == "usajobs":
        return _text(raw.get("JobCategory") or raw.get("JobCategoryName"))
    return _text(raw.get("department") or raw.get("team"))


def normalize_posting(raw: dict[str, Any], source: Source) -> dict[str, Any]:
    """Return one canonical posting row for Greenhouse, Lever, or Ashby."""

    ats = source.ats.lower()
    source_id = _text(raw.get("id") or raw.get("jobId") or raw.get("job_id") or raw.get("PositionID"))
    title = _text(raw.get("title") or raw.get("text") or raw.get("name") or raw.get("PositionTitle"))
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
    else:
        apply_url = _text(raw.get("jobUrl") or raw.get("applyUrl") or raw.get("url"))
        description = strip_html(raw.get("descriptionHtml") or raw.get("description"))
        employment_type = _text(raw.get("employmentType"))
        workplace_type = _text(raw.get("workplaceType"))
        posted_at = _date_or_empty(raw.get("publishedAt"))

    location = _location(source, raw)
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
        "description": description,
        "apply_url": apply_url,
        "posted_at": posted_at,
        "first_seen": "",
        "last_seen": "",
        "removed_date": "",
        "in_role": is_us_location(location) and is_in_role(title, description),
        "is_us": is_us_location(location),
        "first_run": False,
    }

