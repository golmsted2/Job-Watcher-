from jobwatcher.config import SOURCE_BY_ID, Source, is_in_role
from jobwatcher.normalize import normalize_posting


def test_greenhouse_record_becomes_common_schema():
    row = normalize_posting(
        {
            "id": 123,
            "title": "Senior Financial Analyst",
            "location": {"name": "New York, NY"},
            "departments": [{"name": "Finance"}],
            "content": "<p>Own the forecast.</p>",
            "absolute_url": "https://example.test/jobs/123",
            "updated_at": "2026-11-20T12:00:00Z",
        },
        SOURCE_BY_ID["stripe"],
    )

    assert row["posting_key"] == "stripe:123"
    assert row["location"] == "New York, NY"
    assert row["team"] == "Finance"
    assert row["description"] == "Own the forecast."
    assert row["in_role"] is True


def test_lever_categories_and_epoch_timestamp_are_normalized():
    row = normalize_posting(
        {
            "id": "abc",
            "text": "Data Analyst",
            "categories": {"location": "Remote", "team": "Data", "commitment": "Full-time"},
            "descriptionPlain": "Analyze data",
            "hostedUrl": "https://example.test/abc",
            "createdAt": 0,
        },
        Source("lever-test", "Lever Test Employer", "Lever", "https://example.test/lever"),
    )

    assert row["source_id"] == "abc"
    assert row["location"] == "Remote"
    assert row["employment_type"] == "Full-time"
    assert row["posted_at"].startswith("1970-01-01T00:00:00")


def test_role_rule_is_explicit_and_case_insensitive():
    assert is_in_role("VP, FP&A")
    assert is_in_role("Senior Financial Analyst")
    assert is_in_role("Credit Risk Analyst")
    assert not is_in_role("Business Intelligence Manager")
    assert not is_in_role("Data Analyst")
    assert not is_in_role("Senior Product Designer")

