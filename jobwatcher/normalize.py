"""Convert ATS-specific records into the project's common schema."""

from __future__ import annotations

from datetime import datetime, timezone
import html
import re
from typing import Any

from .config import Source, is_in_role


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
    "first_run",
)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(_text(item) for item in value if _text(item))
    if isinstance(value, dict):
        for key in ("name", "label", "text", "title", "location"):
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
    return _text(raw.get("department") or raw.get("team"))


def normalize_posting(raw: dict[str, Any], source: Source) -> dict[str, Any]:
    """Return one canonical posting row for Greenhouse, Lever, or Ashby."""

    ats = source.ats.lower()
    source_id = _text(raw.get("id") or raw.get("jobId") or raw.get("job_id"))
    title = _text(raw.get("title") or raw.get("text") or raw.get("name"))

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
    else:
        apply_url = _text(raw.get("jobUrl") or raw.get("applyUrl") or raw.get("url"))
        description = strip_html(raw.get("descriptionHtml") or raw.get("description"))
        employment_type = _text(raw.get("employmentType"))
        workplace_type = _text(raw.get("workplaceType"))
        posted_at = _date_or_empty(raw.get("publishedAt"))

    return {
        "posting_key": f"{source.id}:{source_id}",
        "employer": source.employer,
        "source": source.id,
        "source_id": source_id,
        "title": title,
        "location": _location(source, raw),
        "team": _team(source, raw),
        "employment_type": employment_type,
        "workplace_type": workplace_type,
        "description": description,
        "apply_url": apply_url,
        "posted_at": posted_at,
        "first_seen": "",
        "last_seen": "",
        "removed_date": "",
        "in_role": is_in_role(title),
        "first_run": False,
    }

