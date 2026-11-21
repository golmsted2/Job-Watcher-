"""Build a deterministic posting history from compressed raw snapshots."""

from __future__ import annotations

from collections import defaultdict
import csv
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
from typing import Any

from .config import OPTIONAL_BOARD_SOURCES, SOURCES, SOURCE_BY_ID, Source
from .normalize import normalize_posting


HISTORY_CSV_FIELDS = (
    "posting_id", "source", "source_id", "employer", "title", "location", "department",
    "posted_date", "url", "in_role", "first_run", "first_seen", "last_seen", "status", "removed_date",
)


def _read_json(path: Path) -> dict[str, Any]:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8"))


def _runs(raw_root: Path) -> list[tuple[str, dict[str, Any], dict[str, Path]]]:
    runs: list[tuple[str, dict[str, Any], dict[str, Path]]] = []
    if not raw_root.exists():
        return runs
    for day_dir in sorted(path for path in raw_root.iterdir() if path.is_dir()):
        status_path = day_dir / "_status.json"
        statuses = _read_json(status_path) if status_path.exists() else {"sources": []}
        raw_files = {path.stem.removesuffix(".json"): path for path in day_dir.glob("*.json.gz")}
        runs.append((day_dir.name, statuses, raw_files))
    return runs


def build_history(raw_root: str | Path) -> list[dict[str, Any]]:
    """Replay source snapshots in date order and return sorted history rows."""

    records: dict[str, dict[str, Any]] = {}
    first_successful_day: dict[str, str] = {}
    runs = _runs(Path(raw_root))

    for day, _statuses, raw_files in runs:
        for source_id, path in raw_files.items():
            first_successful_day.setdefault(source_id, day)
            envelope = _read_json(path)
            source_meta = envelope.get("source")
            if isinstance(source_meta, dict):
                source = Source(
                    source_meta["id"],
                    source_meta["employer"],
                    source_meta["ats"],
                    source_meta.get("endpoint", ""),
                )
            else:
                # Compatibility for snapshots written before source metadata
                # was embedded in each raw file.
                source = SOURCE_BY_ID[source_id]
            listed_keys: set[str] = set()
            for raw_posting in envelope.get("jobs", []):
                normalized = normalize_posting(raw_posting, source)
                # Descriptions stay in the compressed raw evidence.  The site
                # never displays them, so excluding them from history keeps
                # browser downloads small while preserving reproducibility.
                normalized.pop("description", None)
                key = normalized["posting_key"]
                listed_keys.add(key)
                if key not in records:
                    normalized["first_seen"] = day
                    normalized["first_run"] = day == first_successful_day[source_id]
                    normalized["last_seen"] = day
                    records[key] = normalized
                else:
                    record = records[key]
                    for field in (
                        "title", "location", "team", "employment_type", "workplace_type",
                        "salary_min", "salary_max", "salary_currency", "salary_text", "apply_url",
                        "salary_period", "salary_annual_min", "salary_annual_max",
                        "description_excerpt",
                        "posted_at", "in_role", "is_us", "is_internship", "is_new_grad",
                        "sponsorship", "degree_requirement", "program_type", "duplicate_key",
                    ):
                        if normalized[field]:
                            record[field] = normalized[field]
                    record["last_seen"] = day
                    record["removed_date"] = ""

            # A source is allowed to fail.  Only a successful raw snapshot can
            # prove that an omitted posting was removed.
            for record in records.values():
                if record["source"] == source_id and record["removed_date"] == "" and record["posting_key"] not in listed_keys:
                    record["removed_date"] = day

    # When the watchlist changes, the prior employers should not remain open
    # forever just because their last snapshot is still in the repository.
    # Test fixtures and historical-only rebuilds without a current source are
    # left untouched; a live run with at least one active source proves the
    # old feed has been retired from the published watchlist.
    if runs:
        latest_day, latest_status, _ = runs[-1]
        active_ids = {source.id for source in (*SOURCES, *OPTIONAL_BOARD_SOURCES)}
        current_ids = {item.get("id") for item in latest_status.get("sources", []) if item.get("id") in active_ids}
        if current_ids:
            for record in records.values():
                if record["source"] not in active_ids and not record["removed_date"]:
                    record["removed_date"] = latest_day

    return sorted(records.values(), key=lambda row: row["posting_key"])


def load_status_days(raw_root: str | Path) -> list[dict[str, Any]]:
    """Read per-day source statuses, preserving the evidence for the site."""

    return [statuses for _day, statuses, _raw_files in _runs(Path(raw_root))]


def build_status(raw_root: str | Path, history: list[dict[str, Any]], now: datetime | None = None) -> dict[str, Any]:
    statuses = load_status_days(raw_root)
    latest = statuses[-1] if statuses else {"run_date": "", "sources": []}
    latest_date = latest.get("run_date", "")
    successful_days = {item.get("run_date") for item in statuses if item.get("pipeline_ok", True)} - {None, ""}
    raw_days = [item.get("run_date") for item in statuses if item.get("raw_file_count", 0) > 0]
    open_us_rows = [row for row in history if not row["removed_date"] and row.get("is_us", False)]
    open_rows = [row for row in open_us_rows if row.get("in_role", False)]
    open_all_rows = [row for row in history if not row["removed_date"]]
    new_today = [row for row in history if row["first_seen"] == latest_date and not row["first_run"] and row.get("is_us", False) and row.get("in_role", False)]
    removed_today = [row for row in history if row["removed_date"] == latest_date and row.get("is_us", False) and row.get("in_role", False)]
    new_all_today = [row for row in history if row["first_seen"] == latest_date and not row["first_run"]]
    removed_all_today = [row for row in history if row["removed_date"] == latest_date]
    return {
        "run_utc": (now or datetime.now(timezone.utc)).isoformat(),
        "latest_run_date": latest_date,
        "earliest_raw_date": min(raw_days) if raw_days else "",
        "successful_run_days": len(successful_days),
        "open_postings": len(open_rows),
        "open_us_postings": len(open_us_rows),
        "open_all_postings": len(open_all_rows),
        "new_today": len(new_today),
        "removed_today": len(removed_today),
        "new_all_today": len(new_all_today),
        "removed_all_today": len(removed_all_today),
        "first_run_postings": sum(1 for row in history if row["first_run"]),
        "sources": latest.get("sources", []),
    }


def write_json(path: str | Path, payload: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _csv_date(value: Any) -> str:
    text = str(value or "")
    return text[:10] if len(text) >= 10 and text[4] == "-" and text[7] == "-" else ""


def write_history_csv(path: str | Path, history: list[dict[str, Any]]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HISTORY_CSV_FIELDS)
        writer.writeheader()
        for row in sorted(history, key=lambda item: item["posting_key"]):
            writer.writerow({
                "posting_id": row["posting_key"],
                "source": row.get("source", ""),
                "source_id": row.get("source_id", ""),
                "employer": row.get("employer", ""),
                "title": row.get("title", ""),
                "location": row.get("location", ""),
                "department": row.get("team", ""),
                "posted_date": _csv_date(row.get("posted_at")),
                "url": row.get("apply_url", ""),
                "in_role": str(bool(row.get("in_role", False))).lower(),
                "first_run": str(bool(row.get("first_run", False))).lower(),
                "first_seen": row.get("first_seen", ""),
                "last_seen": row.get("last_seen", ""),
                "status": "removed" if row.get("removed_date") else "open",
                "removed_date": row.get("removed_date", ""),
            })


def assignment_status(status: dict[str, Any]) -> dict[str, Any]:
    """Return the exact compact status contract from the project handout."""

    return {
        "run_time": status.get("run_utc", ""),
        "first_run_date": status.get("earliest_raw_date", ""),
        "days_with_success": status.get("successful_run_days", 0),
        "open": status.get("open_all_postings", status.get("open_us_postings", 0)),
        "new_today": status.get("new_all_today", 0),
        "removed_today": status.get("removed_all_today", 0),
        "sources": [
            {
                "name": item.get("employer") or item.get("id", ""),
                "ok": bool(item.get("ok", False)),
                "count": item.get("item_count", 0),
            }
            for item in status.get("sources", [])
        ],
    }


def issue_body(history: list[dict[str, Any]], run_date: str) -> str:
    new_rows = [row for row in history if row["first_seen"] == run_date and not row["first_run"]]
    removed_rows = [row for row in history if row["removed_date"] == run_date]

    def section(title: str, rows: list[dict[str, Any]]) -> str:
        lines = [f"## {title}", ""]
        if not rows:
            return "\n".join(lines + ["None.", ""])
        lines.extend(f"- [{row['title']}]({row['apply_url']}) — {row['employer']} · {row['location']}" for row in rows)
        lines.append("")
        return "\n".join(lines)

    return f"# Job changes for {run_date}\n\n{section('New postings', new_rows)}{section('Removed postings', removed_rows)}"

