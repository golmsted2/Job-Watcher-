"""Daily source fetch, raw snapshot, history, and status pipeline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
from urllib.request import Request, urlopen

from .config import SOURCES, Source
from .history import build_history, build_status, issue_body, write_json


def fetch_json(source: Source, timeout: int = 60) -> list[dict]:
    request = Request(source.endpoint, headers={"User-Agent": "FDA-Job-Watcher/0.1 (+GitHub Actions)"})
    with urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if isinstance(payload, list):
        return payload
    for key in ("jobs", "postings", "results", "data"):
        if isinstance(payload.get(key), list):
            return payload[key]
    return []


def _write_gzip_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)


def build_outputs(
    *,
    raw_root: str | Path = "data/raw",
    processed_root: str | Path = "data/processed",
    site_data_root: str | Path = "site/data",
) -> dict:
    """Rebuild published files from raw evidence without calling employers."""

    history = build_history(raw_root)
    status = build_status(raw_root, history)
    processed = Path(processed_root)
    site_data = Path(site_data_root)
    write_json(processed / "history.json", history)
    write_json(processed / "status.json", status)
    write_json(site_data / "history.json", history)
    write_json(site_data / "status.json", status)
    issue_date = status.get("latest_run_date") or datetime.now(timezone.utc).date().isoformat()
    (processed / "issue.md").write_text(issue_body(history, issue_date), encoding="utf-8")
    return status


def run_pipeline(
    *,
    run_date: str | None = None,
    raw_root: str | Path = "data/raw",
    processed_root: str | Path = "data/processed",
    site_data_root: str | Path = "site/data",
    sources: tuple[Source, ...] = SOURCES,
) -> dict:
    day = run_date or datetime.now(timezone.utc).date().isoformat()
    run_utc = datetime.now(timezone.utc).isoformat()
    day_dir = Path(raw_root) / day
    day_dir.mkdir(parents=True, exist_ok=True)
    statuses: list[dict] = []
    raw_file_count = 0

    for source in sources:
        status = {
            "id": source.id,
            "employer": source.employer,
            "ats": source.ats,
            "endpoint": source.endpoint,
            "ok": False,
            "item_count": 0,
            "error": "",
            "fetched_at_utc": run_utc,
        }
        try:
            jobs = fetch_json(source)
            _write_gzip_json(day_dir / f"{source.id}.json.gz", {
                "source": {"id": source.id, "employer": source.employer, "ats": source.ats, "endpoint": source.endpoint},
                "run_date": day,
                "jobs": jobs,
            })
            status["ok"] = True
            status["item_count"] = len(jobs)
            raw_file_count += 1
        except Exception as exc:  # one source must never stop the run
            status["error"] = f"{type(exc).__name__}: {exc}"
        statuses.append(status)

    write_json(day_dir / "_status.json", {
        "run_date": day,
        "run_utc": run_utc,
        "pipeline_ok": True,
        "raw_file_count": raw_file_count,
        "sources": statuses,
    })

    return build_outputs(raw_root=raw_root, processed_root=processed_root, site_data_root=site_data_root)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="UTC run date in YYYY-MM-DD format")
    parser.add_argument("--build-only", action="store_true", help="rebuild outputs from existing raw files without fetching")
    args = parser.parse_args()
    status = build_outputs() if args.build_only else run_pipeline(run_date=args.date)
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()

