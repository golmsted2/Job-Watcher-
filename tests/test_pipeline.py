import json

from jobwatcher.config import Source
from jobwatcher import pipeline


def test_pipeline_continues_after_one_source_fails(tmp_path, monkeypatch):
    sources = (
        Source("stripe", "Stripe", "Greenhouse", "https://example.test/stripe"),
        Source("airbnb", "Airbnb", "Greenhouse", "https://example.test/airbnb"),
    )

    def fake_fetch(source):
        if source.id == "airbnb":
            raise RuntimeError("blocked")
        return [{"id": "1", "title": "Financial Analyst", "location": {"name": "New York, NY"}, "absolute_url": "https://example.test/1"}]

    monkeypatch.setattr(pipeline, "fetch_json", fake_fetch)
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    site = tmp_path / "site-data"
    status = pipeline.run_pipeline(run_date="2026-11-20", raw_root=raw, processed_root=processed, site_data_root=site, sources=sources)

    assert (raw / "2026-11-20" / "stripe.json.gz").exists()
    assert not (raw / "2026-11-20" / "airbnb.json.gz").exists()
    assert status["open_postings"] == 1
    assert [source["ok"] for source in status["sources"]] == [True, False]
    assert json.loads((processed / "history.json").read_text())[0]["title"] == "Financial Analyst"
    assert (site / "status.json").exists()

