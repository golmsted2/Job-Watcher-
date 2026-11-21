from jobwatcher.alerts import build_alert


def test_build_alert_includes_new_matching_roles_and_salary():
    subject, text, html = build_alert(
        [{
            "title": "Financial Analyst",
            "employer": "Test Bank",
            "location": "Chicago, IL",
            "salary_text": "$70,000–$80,000",
            "apply_url": "https://example.test/job/1",
            "first_seen": "2026-11-20",
            "first_run": False,
            "is_us": True,
            "in_role": True,
            "removed_date": "",
        }],
        {"latest_run_date": "2026-11-20"},
    )

    assert "1 new finance roles" in subject
    assert "Test Bank" in text
    assert "$70,000" in html


def test_build_alert_says_when_no_new_roles_exist():
    subject, text, html = build_alert([], {"latest_run_date": "2026-11-20"})

    assert "0 new finance roles" in subject
    assert "No new" in text
    assert "No new" in html
