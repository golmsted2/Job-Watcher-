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
    site: str = ""
    domain: str = ""
    apply_base: str = ""
    max_items: int = 200
    query: str = ""


SOURCES = (
    Source("edward-jones", "Edward Jones", "MCloud", "https://jobsapi-internal.m-cloud.io/api/job?organization=2144&limit=200", max_items=200),
    Source("stifel", "Stifel", "Jibe", "https://join.stifel.com/api/jobs", max_items=200),
    Source(
        "jpmorgan-chase",
        "JPMorgan Chase",
        "Oracle",
        "https://jpmc.fa.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
        site="CX_1001",
        apply_base="https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001",
        max_items=400,
    ),
    Source(
        "bank-of-america",
        "Bank of America",
        "Workday",
        "https://ghr.wd1.myworkdayjobs.com/wday/cxs/ghr/Lateral-US/jobs",
        apply_base="https://ghr.wd1.myworkdayjobs.com/en-US/Lateral-US",
        max_items=400,
        query="finance",
    ),
    Source(
        "citi",
        "Citi",
        "Eightfold",
        "https://citi.eightfold.ai/api/pcsx/search",
        domain="citi.com",
        apply_base="https://citi.eightfold.ai",
        max_items=100,
    ),
    Source(
        "wells-fargo",
        "Wells Fargo",
        "Workday",
        "https://wd1.myworkdaysite.com/wday/cxs/wf/WellsFargoJobs/jobs",
        apply_base="https://wd1.myworkdaysite.com/recruiting/wf/WellsFargoJobs",
        max_items=400,
    ),
    Source(
        "goldman-sachs",
        "Goldman Sachs",
        "Oracle",
        "https://hdpc.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
        site="CX_3001",
        apply_base="https://hdpc.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_3001",
        max_items=400,
    ),
    Source(
        "morgan-stanley",
        "Morgan Stanley",
        "Eightfold",
        "https://morganstanley.eightfold.ai/api/pcsx/search",
        domain="morganstanley.com",
        apply_base="https://morganstanley.eightfold.ai",
        max_items=100,
    ),
    Source("pnc", "PNC", "Phenom", "https://careers.pnc.com/widgets", max_items=400),
    Source("us-bank", "U.S. Bank", "Phenom", "https://careers.usbank.com/widgets", max_items=400),
    Source("state-street", "State Street", "Phenom", "https://careers.statestreet.com/widgets", max_items=1000),
    Source(
        "bny",
        "BNY",
        "Oracle",
        "https://eofe.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
        site="BNY-Careers",
        apply_base="https://eofe.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/BNY-Careers",
        max_items=400,
    ),
    Source(
        "american-express",
        "American Express",
        "Oracle",
        "https://egug.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions",
        site="CX_1",
        apply_base="https://egug.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1",
        max_items=400,
    ),
    Source(
        "capital-one",
        "Capital One",
        "Workday",
        "https://capitalone.wd12.myworkdayjobs.com/wday/cxs/capitalone/Capital_One/jobs",
        apply_base="https://capitalone.wd12.myworkdayjobs.com/en-US/Capital_One",
        max_items=400,
        query="finance",
    ),
    Source(
        "northern-trust",
        "Northern Trust",
        "Workday",
        "https://ntrs.wd1.myworkdayjobs.com/wday/cxs/ntrs/northerntrust/jobs",
        apply_base="https://ntrs.wd1.myworkdayjobs.com/en-US/northerntrust",
        max_items=400,
    ),
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
    "A posting is in-role when it is in the United States, contains finance, banking, "
    "investment, accounting, credit, or risk language, and is early-career or close to entry level."
)
ROLE_TERMS = re.compile(
    r"\b(?:finance|financial|fp&a|corporate finance|investment banking|banking|banker|"
    r"treasury|credit|credit risk|financial risk|risk management|valuation|"
    r"portfolio|investment|accounting|accountant|controller|quantitative finance|"
    r"wealth management|asset management|capital markets|financial planning|economics|"
    r"fund accounting|investment operations|commercial banking|lending|loans?|mortgage|"
    r"securities|brokerage|payments|collections|client service|markets?)\b",
    re.IGNORECASE,
)
EARLY_CAREER_TERMS = re.compile(
    r"\b(?:analyst|associate|coordinator|specialist|assistant|junior|rotational|"
    r"new grad(?:uate)?|entry[- ]level|early career|graduate|campus|university|"
    r"intern(?:ship)?|trainee|representative|advisor|banker)\b",
    re.IGNORECASE,
)
SENIOR_TERMS = re.compile(
    r"\b(?:senior|sr\.?|lead|principal|staff|manager|director|head|vice president|vp|"
    r"avp|svp|evp|chief|executive)\b",
    re.IGNORECASE,
)
EXPERIENCE_TERMS = re.compile(r"\b(?:[3-9]|[1-9]\d)\+?\s*(?:years?|yrs?)\b", re.IGNORECASE)


US_STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
}
US_STATE_NAMES = {
    "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware",
    "florida", "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky",
    "louisiana", "maine", "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri",
    "montana", "nebraska", "nevada", "new hampshire", "new jersey", "new mexico", "new york",
    "north carolina", "north dakota", "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island",
    "south carolina", "south dakota", "tennessee", "texas", "utah", "vermont", "virginia", "washington",
    "west virginia", "wisconsin", "wyoming", "district of columbia",
}
US_MARKERS = re.compile(r"\b(?:united states|u\.s\.a?\.?|usa|us)\b", re.IGNORECASE)
NON_US_MARKERS = re.compile(
    r"\b(?:canada|mexico|ireland|united kingdom|uk|england|scotland|wales|india|"
    r"philippines|singapore|australia|germany|france|spain|italy|china|japan|"
    r"brazil|poland|netherlands|belgium|switzerland|hong kong|south africa|"
    r"new zealand|malaysia|thailand|israel|uae|united arab emirates)\b",
    re.IGNORECASE,
)


def is_us_location(location: str) -> bool:
    """Return true only for an explicit US location, not ambiguous 'Remote'."""

    value = (location or "").strip()
    if not value:
        return False
    if US_MARKERS.search(value):
        return True
    if NON_US_MARKERS.search(value):
        return False
    if any(re.search(rf"\b{re.escape(state)}\b", value, re.IGNORECASE) for state in US_STATE_NAMES):
        return True
    # Only accept a state abbreviation when it is a comma-delimited location
    # component. This avoids treating "Co." in "Dublin, Co. Dublin, Ireland"
    # as Colorado.
    state_tokens = re.findall(r"(?:^|[,/])\s*([A-Za-z]{2})(?=\s*(?:,|$|\d))", value.upper())
    return any(token in US_STATE_CODES for token in state_tokens)


def is_early_career(title: str, description: str = "") -> bool:
    """Match entry-level or near-entry-level titles while excluding senior roles."""

    title_text = title or ""
    description_text = description or ""
    if SENIOR_TERMS.search(title_text) or EXPERIENCE_TERMS.search(title_text) or EXPERIENCE_TERMS.search(description_text):
        return False
    return bool(EARLY_CAREER_TERMS.search(title_text))


def is_in_role(title: str, description: str = "") -> bool:
    """Return whether a posting matches the finance-only early-career rule."""

    finance_text = f"{title or ''} {description or ''}"
    return bool(ROLE_TERMS.search(finance_text)) and is_early_career(title, description)


 # The two aliases keep older raw fixtures readable after the finance watchlist
 # replaced the original demo sources. They are not active watchlist entries.
SOURCE_BY_ID = {source.id: source for source in (*SOURCES, *OPTIONAL_BOARD_SOURCES)}
SOURCE_BY_ID.update({
    "stripe": Source("stripe", "Stripe", "Greenhouse", "https://example.test/stripe"),
    "airbnb": Source("airbnb", "Airbnb", "Greenhouse", "https://example.test/airbnb"),
})

