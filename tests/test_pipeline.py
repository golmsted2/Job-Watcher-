import json

from jobwatcher.config import Source
from jobwatcher import pipeline
from jobwatcher.normalize import _salary_from_text


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
    def fail_if_html_is_fetched(_url):
        raise AssertionError("the scheduled assignment pipeline must not read job-page HTML")

    monkeypatch.setattr(pipeline, "_fetch_salary_page", fail_if_html_is_fetched)
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
    assert (tmp_path / "history.csv").exists()
    assert json.loads((tmp_path / "status.json").read_text())["open"] == 1


def test_salary_enrichment_uses_cached_public_page_values(monkeypatch):
    source = Source("test-bank", "Test Bank", "Workday", "https://example.test/jobs")
    jobs = [{
        "title": "Financial Analyst",
        "locationsText": "Chicago, IL",
        "externalPath": "/job/1",
        "bulletFields": ["1"],
        "_apply_url": "https://example.test/job/1",
    }]
    calls = []

    def fake_salary(url):
        calls.append(url)
        return 60000, 75000, "USD", "$60,000–$75,000 annual"

    monkeypatch.setattr(pipeline, "_fetch_salary_page", fake_salary)
    cache = {}
    enriched, count = pipeline._enrich_salary_pages(source, jobs, cache)

    assert count == 1
    assert calls == ["https://example.test/job/1"]
    assert enriched[0]["_salary_enriched"]["min"] == 60000
    assert cache["test-bank:1"]["text"] == "$60,000–$75,000 annual"


def test_salary_text_parser_prefers_the_published_range():
    html = "<p>Hours Per Week: 40</p><p>Pay Transparency details</p><p>Pay range $70,000.00 - $150,000.00 annualized salary</p>"

    assert _salary_from_text(html) == (70000, 150000, "USD", "$70,000–$150,000 annual")

