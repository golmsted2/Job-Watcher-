import gzip
import json

from jobwatcher.history import assignment_status, build_history, build_status, write_history_csv, write_json


def _write_snapshot(root, day, jobs, *, ok=True):
    day_dir = root / day
    day_dir.mkdir(parents=True)
    write_json(
        day_dir / "_status.json",
        {
            "run_date": day,
            "pipeline_ok": True,
            "raw_file_count": 1 if ok else 0,
            "sources": [{"id": "stripe", "ok": ok, "item_count": len(jobs) if ok else 0}],
        },
    )
    if ok:
        with gzip.open(day_dir / "stripe.json.gz", "wt", encoding="utf-8") as handle:
            json.dump({"source": "stripe", "run_date": day, "jobs": jobs}, handle)


def test_history_replay_marks_removals_and_reopens_without_resetting_first_seen(tmp_path):
    raw = tmp_path / "raw"
    job_a = {"id": "a", "title": "Financial Analyst", "location": {"name": "Remote"}, "absolute_url": "https://example.test/a"}
    job_b = {"id": "b", "title": "Product Designer", "location": {"name": "Austin"}, "absolute_url": "https://example.test/b"}
    _write_snapshot(raw, "2026-11-17", [job_a, job_b])
    _write_snapshot(raw, "2026-11-18", [job_b])
    _write_snapshot(raw, "2026-11-19", [], ok=False)
    _write_snapshot(raw, "2026-11-20", [job_a, job_b])

    history = build_history(raw)
    by_id = {row["source_id"]: row for row in history}

    assert by_id["a"]["first_seen"] == "2026-11-17"
    assert by_id["a"]["first_run"] is True
    assert by_id["a"]["removed_date"] == ""
    assert by_id["a"]["last_seen"] == "2026-11-20"
    assert by_id["b"]["removed_date"] == ""


def test_failed_source_does_not_mark_jobs_removed(tmp_path):
    raw = tmp_path / "raw"
    job = {"id": "a", "title": "Financial Analyst", "absolute_url": "https://example.test/a"}
    _write_snapshot(raw, "2026-11-17", [job])
    _write_snapshot(raw, "2026-11-18", [], ok=False)

    history = build_history(raw)
    assert history[0]["removed_date"] == ""
    status = build_status(raw, history)
    assert status["successful_run_days"] == 2


def test_assignment_exports_use_the_professor_contract(tmp_path):
    raw = tmp_path / "raw"
    job = {"id": "a", "title": "Financial Analyst", "location": {"name": "Austin, TX"}, "absolute_url": "https://example.test/a"}
    _write_snapshot(raw, "2026-11-17", [job])
    history = build_history(raw)
    csv_path = tmp_path / "history.csv"
    write_history_csv(csv_path, history)
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert header == "posting_id,source,source_id,employer,title,location,department,posted_date,url,in_role,first_run,first_seen,last_seen,status,removed_date"
    compact = assignment_status(build_status(raw, history))
    assert set(compact) == {"run_time", "first_run_date", "days_with_success", "open", "new_today", "removed_today", "sources"}
    assert compact["sources"] == [{"name": "stripe", "ok": True, "count": 1}]

