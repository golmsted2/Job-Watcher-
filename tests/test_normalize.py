import pytest

from jobwatcher.config import Source, is_in_role, is_us_location
from jobwatcher.normalize import normalize_posting


def test_greenhouse_record_becomes_common_schema():
    row = normalize_posting(
        {
            "id": 123,
            "title": "Financial Analyst",
            "location": {"name": "New York, NY"},
            "departments": [{"name": "Finance"}],
            "content": "<p>Own the forecast.</p>",
            "absolute_url": "https://example.test/jobs/123",
            "updated_at": "2026-11-20T12:00:00Z",
        },
        Source("greenhouse-test", "Test Bank", "Greenhouse", "https://example.test/greenhouse"),
    )

    assert row["posting_key"] == "greenhouse-test:123"
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
    assert is_in_role("FP&A Analyst")
    assert not is_in_role("Senior Financial Analyst")
    assert is_in_role("Credit Risk Analyst")
    assert is_in_role("Client Service Associate", "Supports investment portfolios and financial markets.")
    assert is_in_role("Relationship Banker")
    assert not is_in_role("Business Intelligence Manager")
    assert not is_in_role("Data Analyst")
    assert not is_in_role("Senior Product Designer")


def test_us_location_rule_rejects_ambiguous_remote_and_non_us_locations():
    assert is_us_location("New York, NY")
    assert is_us_location("Remote, United States")
    assert is_us_location("Boston, Massachusetts")
    assert not is_us_location("Remote")
    assert not is_us_location("London, UK")
    assert not is_us_location("Dublin, Co. Dublin, Ireland")


def test_adzuna_adapter_uses_dynamic_employer_and_us_location():
    row = normalize_posting(
        {
            "id": "adz-1",
            "title": "Financial Analyst",
            "location": {"display_name": "Boston, MA"},
            "company": {"display_name": "Example Bank"},
            "description": "Entry-level finance role.",
            "redirect_url": "https://example.test/adz-1",
            "created": "2026-11-20T12:00:00Z",
        },
        Source("adzuna-us", "Adzuna", "Adzuna", "https://example.test/adzuna"),
    )

    assert row["employer"] == "Example Bank"
    assert row["is_us"] is True
    assert row["in_role"] is True


def test_workday_record_maps_to_a_us_early_career_posting():
    row = normalize_posting(
        {
            "title": "Credit Analyst - Early Career",
            "externalPath": "/job/Richmond-VA/Credit-Analyst_R123",
            "locationsText": "Richmond, VA",
            "bulletFields": ["R123"],
            "timeType": "Full time",
            "_apply_url": "https://example.test/job/R123",
        },
        Source("workday-test", "Test Bank", "Workday", "https://example.test/jobs"),
    )

    assert row["posting_key"] == "workday-test:R123"
    assert row["is_us"] is True
    assert row["in_role"] is True
    assert row["apply_url"].endswith("R123")


def test_oracle_record_maps_finance_and_secondary_source_fields():
    row = normalize_posting(
        {
            "Id": "456",
            "Title": "2027 Summer Analyst - Finance",
            "PrimaryLocation": "New York, NY, United States",
            "JobFunction": "Finance",
            "ShortDescriptionStr": "A campus role for new graduates.",
            "PostedDate": "2026-11-20",
            "_apply_url": "https://example.test/job/456",
        },
        Source("oracle-test", "Test Bank", "Oracle", "https://example.test/oracle", site="CX"),
    )

    assert row["posting_key"] == "oracle-test:456"
    assert row["team"] == "Finance"
    assert row["in_role"] is True


def test_normalize_adds_salary_and_early_career_signals():
    row = normalize_posting(
        {
            "id": "salary-1",
            "title": "2027 Credit Analyst Program",
            "location": {"name": "Dallas, TX"},
            "content": "Recent graduates welcome. Bachelor's degree required. Visa sponsorship available.",
            "salary": {"min": 72000, "max": 88000, "currency": "USD"},
            "absolute_url": "https://example.test/salary-1",
        },
        Source("greenhouse-test", "Test Bank", "Greenhouse", "https://example.test/greenhouse"),
    )

    assert row["salary_min"] == 72000
    assert row["salary_max"] == 88000
    assert row["salary_currency"] == "USD"
    assert row["salary_period"] == "year"
    assert row["salary_annual_min"] == 72000
    assert row["salary_annual_max"] == 88000
    assert row["is_new_grad"] is True
    assert row["program_type"] == "New graduate program"
    assert row["description_excerpt"].startswith("Recent graduates")
    assert row["sponsorship"] == "mentioned"
    assert row["degree_requirement"] == "mentioned"
    assert row["duplicate_key"] == "test bank 2027 credit analyst program dallas tx"


def test_normalize_extracts_salary_range_from_published_description():
    row = normalize_posting(
        {
            "id": "phenom-salary-1",
            "title": "Financial Analyst",
            "location": "Chicago, IL",
            "description": "Salary Range: $55,000 - $65,000 Annual. Benefits included.",
            "applyUrl": "https://example.test/phenom-salary-1",
        },
        Source("phenom-test", "Test Bank", "Phenom", "https://example.test/jobs"),
    )

    assert row["salary_min"] == 55000
    assert row["salary_max"] == 65000
    assert row["salary_currency"] == "USD"
    assert row["salary_period"] == "year"
    assert row["salary_text"] == "$55,000–$65,000 annual"


@pytest.mark.parametrize(
    "source, raw, expected_location",
    [
        (
            Source("mcloud-test", "MCloud Bank", "MCloud", "https://example.test/mcloud"),
            {"job_id": "m1", "title": "Financial Analyst", "primary_city": "St. Louis", "primary_state": "MO", "primary_country": "United States", "function": "Finance", "url": "https://example.test/m1"},
            "St. Louis, MO, United States",
        ),
        (
            Source("jibe-test", "Jibe Bank", "Jibe", "https://example.test/jibe"),
            {"job_id": "j1", "title": "Credit Analyst", "location": "Chicago, IL", "department": "Credit", "apply_url": "https://example.test/j1"},
            "Chicago, IL",
        ),
        (
            Source("eightfold-test", "Eightfold Bank", "Eightfold", "https://example.test/eightfold"),
            {"job_id": "e1", "title": "Investment Analyst", "locations": "New York, NY", "department": "Investments", "positionUrl": "https://example.test/e1"},
            "New York, NY",
        ),
        (
            Source("phenom-test", "Phenom Bank", "Phenom", "https://example.test/phenom"),
            {"req_id": "p1", "title": "Relationship Banker", "city": "Pittsburgh", "state": "PA", "country": "United States", "category": "Banking", "applyUrl": "https://example.test/p1"},
            "Pittsburgh, PA, United States",
        ),
    ],
)
def test_active_watchlist_adapters_map_to_common_columns(source, raw, expected_location):
    row = normalize_posting(raw, source)

    assert row["posting_key"].startswith(f"{source.id}:")
    assert row["location"] == expected_location
    assert row["apply_url"].startswith("https://example.test/")
    assert row["in_role"] is True


