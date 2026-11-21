"""Project configuration and the watch list.

The watch list intentionally keeps the ATS and public JSON endpoint visible in
one place.  If an employer changes ATS providers, only this file and its
adapter tests need to change.
"""

from dataclasses import dataclass
import os
import re


@dataclass(frozen=True)
class Source:
    id: str
    employer: str
    ats: str
    endpoint: str
    enabled: bool = True


SOURCES = (
    Source("airbnb", "Airbnb", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs?content=true"),
    Source("stripe", "Stripe", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"),
    Source("datadog", "Datadog", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/datadog/jobs?content=true"),
    Source("coinbase", "Coinbase", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/coinbase/jobs?content=true"),
    Source("figma", "Figma", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true"),
    Source("lyft", "Lyft", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/lyft/jobs?content=true"),
    Source("asana", "Asana", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/asana/jobs?content=true"),
    Source("intercom", "Intercom", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/intercom/jobs?content=true"),
    Source("duolingo", "Duolingo", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/duolingo/jobs?content=true"),
    Source("pinterest", "Pinterest", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/pinterest/jobs?content=true"),
    Source("robinhood", "Robinhood", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/robinhood/jobs?content=true"),
    Source("brex", "Brex", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/brex/jobs?content=true"),
    Source("gitlab", "GitLab", "Greenhouse", "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true"),
    Source("openai", "OpenAI", "Ashby", "https://api.ashbyhq.com/posting-api/job-board/openai"),
    Source("linear", "Linear", "Ashby", "https://api.ashbyhq.com/posting-api/job-board/linear"),
)


OPTIONAL_BOARD_SOURCES = (
    Source("adzuna-us", "Adzuna", "Adzuna", "https://api.adzuna.com/v1/api/jobs/us/search/1"),
    Source("jooble-us", "Jooble", "Jooble", "https://jooble.org/api"),
    Source("usajobs", "USAJOBS", "USAJOBS", "https://data.usajobs.gov/api/search"),
)


def configured_sources() -> tuple[Source, ...]:
    """Return ATS sources plus optional board APIs whose secrets are present."""

    sources = list(SOURCES)
    if os.getenv("ADZUNA_APP_ID") and os.getenv("ADZUNA_APP_KEY"):
        sources.append(OPTIONAL_BOARD_SOURCES[0])
    if os.getenv("JOOBLE_API_KEY"):
        sources.append(OPTIONAL_BOARD_SOURCES[1])
    if os.getenv("USAJOBS_API_KEY") and os.getenv("USAJOBS_EMAIL"):
        sources.append(OPTIONAL_BOARD_SOURCES[2])
    return tuple(sources)


# This is deliberately transparent and editable.  It is applied to every
# posting after source-specific normalization, including postings outside the
# target role so Browse can offer an "all postings" view.
ROLE_RULE_DESCRIPTION = (
    "A posting is in-role when it is in the United States, contains finance-specific "
    "language, and is early-career or close to entry level."
)
ROLE_TERMS = re.compile(
    r"\b(?:finance|financial|fp&a|corporate finance|investment banking|"
    r"treasury|credit|credit risk|financial risk|risk management|valuation|"
    r"portfolio|investment|accounting|accountant|controller|quantitative finance)\b",
    re.IGNORECASE,
)
EARLY_CAREER_TERMS = re.compile(
    r"\b(?:analyst|associate|coordinator|specialist|assistant|junior|rotational|"
    r"new grad(?:uate)?|entry[- ]level|early career|graduate|campus|university)\b",
    re.IGNORECASE,
)
SENIOR_TERMS = re.compile(
    r"\b(?:senior|sr\.?|lead|principal|staff|manager|director|head|vice president|vp|chief|executive)\b",
    re.IGNORECASE,
)
EXPERIENCE_TERMS = re.compile(r"\b(?:[3-9]|[1-9]\d)\+?\s*(?:years?|yrs?)\b", re.IGNORECASE)


US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
}
US_MARKERS = re.compile(r"\b(?:united states|u\.s\.a?\.?|usa|us)\b", re.IGNORECASE)


def is_us_location(location: str) -> bool:
    """Return true only for an explicit US location, not ambiguous 'Remote'."""

    value = (location or "").strip()
    if not value:
        return False
    if US_MARKERS.search(value):
        return True
    tokens = re.findall(r"\b[A-Za-z]{2}\b", value.upper())
    return any(token in US_STATE_CODES for token in tokens)


def is_early_career(title: str, description: str = "") -> bool:
    """Match entry-level or near-entry-level titles while excluding senior roles."""

    title_text = title or ""
    if SENIOR_TERMS.search(title_text) or EXPERIENCE_TERMS.search(title_text):
        return False
    return bool(EARLY_CAREER_TERMS.search(title_text))


def is_in_role(title: str, description: str = "") -> bool:
    """Return whether a posting matches the finance-only early-career rule."""

    return bool(ROLE_TERMS.search(title or "")) and is_early_career(title, description)


SOURCE_BY_ID = {source.id: source for source in (*SOURCES, *OPTIONAL_BOARD_SOURCES)}

