"""Daily source fetch, raw snapshot, history, and status pipeline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import time
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .config import Source, configured_sources
from .history import build_history, build_status, issue_body, write_json


def _read_json(request: Request, timeout: int) -> object:
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _apply_url(source: Source, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{source.apply_base.rstrip('/')}/{path.lstrip('/')}" if source.apply_base else path


def _fetch_workday(source: Source, headers: dict[str, str], timeout: int) -> list[dict]:
    rows: list[dict] = []
    page_size = 20
    for offset in range(0, source.max_items, page_size):
        payload = json.dumps({
            "limit": page_size,
            "offset": offset,
            "searchText": source.query,
            "appliedFacets": {},
        }).encode("utf-8")
        request = Request(
            source.endpoint,
            data=payload,
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
        response = _read_json(request, timeout)
        page = response.get("jobPostings", []) if isinstance(response, dict) else []
        if not page:
            break
        for row in page:
            if source.apply_base and row.get("externalPath"):
                row["_apply_url"] = _apply_url(source, row["externalPath"])
        rows.extend(page)
        if len(page) < page_size:
            break
    return rows[: source.max_items]


def _oracle_url(source: Source, offset: int, limit: int) -> str:
    finder = f"findReqs;siteNumber={source.site},limit={limit},offset={offset},sortBy=POSTING_DATES_DESC"
    query = urlencode({
        "onlyData": "true",
        "expand": "requisitionList.secondaryLocations",
        "finder": finder,
    })
    parts = urlsplit(source.endpoint)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))


def _fetch_oracle(source: Source, headers: dict[str, str], timeout: int) -> list[dict]:
    rows: list[dict] = []
    page_size = 200
    for offset in range(0, source.max_items, page_size):
        request = Request(_oracle_url(source, offset, min(page_size, source.max_items - offset)), headers=headers)
        payload = _read_json(request, timeout)
        items = payload.get("items", []) if isinstance(payload, dict) else []
        page: list[dict] = []
        total = 0
        for item in items:
            total = int(item.get("TotalJobsCount") or 0)
            for row in item.get("requisitionList", []) or []:
                if source.apply_base and row.get("Id"):
                    row["_apply_url"] = f"{source.apply_base.rstrip('/')}/job/{row['Id']}"
                page.append(row)
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size or (total and offset + len(page) >= total):
            break
    return rows[: source.max_items]


def _fetch_phenom(source: Source, headers: dict[str, str], timeout: int) -> list[dict]:
    rows: list[dict] = []
    page_size = min(100, source.max_items)
    for offset in range(0, source.max_items, page_size):
        payload = json.dumps({
            "ddoKey": "refineSearch",
            "jobs": True,
            "from": offset,
            "size": page_size,
            "sort": {"order": "desc", "field": "dateCreated"},
        }).encode("utf-8")
        request = Request(
            source.endpoint,
            data=payload,
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
        response = _read_json(request, timeout)
        refine = response.get("refineSearch", {}) if isinstance(response, dict) else {}
        data = refine.get("data", {}) if isinstance(refine, dict) else {}
        page = data.get("jobs", []) if isinstance(data, dict) else []
        if not page:
            break
        rows.extend(page)
        if len(page) < page_size:
            break
    return rows[: source.max_items]


def _fetch_eightfold(source: Source, headers: dict[str, str], timeout: int) -> list[dict]:
    rows: list[dict] = []
    page_size = 10
    for start in range(0, source.max_items, page_size):
        if start:
            time.sleep(1)
        query = urlencode({
            "domain": source.domain,
            "query": "",
            "location": "",
            "start": start,
        })
        request = Request(f"{source.endpoint}?{query}", headers=headers)
        for attempt in range(3):
            try:
                response = _read_json(request, timeout)
                break
            except HTTPError as exc:
                if exc.code != 429 or attempt == 2:
                    raise
                time.sleep(3 * (attempt + 1))
        data = response.get("data", {}) if isinstance(response, dict) else {}
        page = data.get("positions", []) if isinstance(data, dict) else []
        if not page:
            break
        for row in page:
            if source.apply_base and row.get("positionUrl"):
                row["_apply_url"] = _apply_url(source, row["positionUrl"])
        rows.extend(page)
        if len(page) < page_size:
            break
    return rows[: source.max_items]


def _fetch_jibe(source: Source, headers: dict[str, str], timeout: int) -> list[dict]:
    rows: list[dict] = []
    page_size = min(100, source.max_items)
    page_number = 1
    while len(rows) < source.max_items:
        query = urlencode({"page": page_number, "limit": page_size})
        request = Request(f"{source.endpoint}?{query}", headers=headers)
        response = _read_json(request, timeout)
        page = response.get("jobs", []) if isinstance(response, dict) else []
        flattened = [job.get("data", job) if isinstance(job, dict) else job for job in page]
        if not flattened:
            break
        rows.extend(flattened)
        if len(flattened) < page_size:
            break
        page_number += 1
    return rows[: source.max_items]


def _fetch_mcloud(source: Source, headers: dict[str, str], timeout: int) -> list[dict]:
    request = Request(source.endpoint, headers=headers)
    response = _read_json(request, timeout)
    if not isinstance(response, dict):
        return []
    return response.get("queryResult", [])[: source.max_items]


def fetch_json(source: Source, timeout: int = 60) -> list[dict]:
    ats = source.ats.lower()
    headers = {"User-Agent": "FDA-Job-Watcher/0.1 (+GitHub Actions)", "Accept": "application/json"}
    if ats == "workday":
        return _fetch_workday(source, headers, timeout)
    if ats == "oracle":
        return _fetch_oracle(source, headers, timeout)
    if ats == "phenom":
        return _fetch_phenom(source, headers, timeout)
    if ats == "eightfold":
        return _fetch_eightfold(source, headers, timeout)
    if ats == "jibe":
        return _fetch_jibe(source, headers, timeout)
    if ats == "mcloud":
        return _fetch_mcloud(source, headers, timeout)
    if ats == "adzuna":
        params = {
            "app_id": os.environ["ADZUNA_APP_ID"],
            "app_key": os.environ["ADZUNA_APP_KEY"],
            "results_per_page": "100",
            "what": "finance analyst",
            "where": "United States",
            "content-type": "application/json",
        }
        request = Request(f"{source.endpoint}?{urlencode(params)}", headers=headers)
    elif ats == "jooble":
        request = Request(
            f"{source.endpoint.rstrip('/')}/{os.environ['JOOBLE_API_KEY']}",
            data=json.dumps({"keywords": "finance analyst", "location": "United States", "page": 1, "ResultOnPage": 100}).encode("utf-8"),
            headers={**headers, "Content-Type": "application/json"},
            method="POST",
        )
    elif ats == "usajobs":
        params = urlencode({"Keyword": "finance analyst", "LocationName": "United States", "ResultsPerPage": "500"})
        request = Request(
            f"{source.endpoint}?{params}",
            headers={**headers, "User-Agent": os.environ["USAJOBS_EMAIL"], "Authorization-Key": os.environ["USAJOBS_API_KEY"]},
        )
    else:
        request = Request(source.endpoint, headers=headers)
    payload = _read_json(request, timeout)
    if ats == "usajobs":
        items = payload.get("SearchResult", {}).get("SearchResultItems", [])
        return [item.get("MatchedObjectDescriptor", item) for item in items]
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
    sources: tuple[Source, ...] | None = None,
) -> dict:
    if sources is None:
        sources = configured_sources()
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

