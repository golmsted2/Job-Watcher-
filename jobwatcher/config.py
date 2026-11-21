"""Project configuration and the watch list.

The watch list intentionally keeps the ATS and public JSON endpoint visible in
one place.  If an employer changes ATS providers, only this file and its
adapter tests need to change.
"""

from dataclasses import dataclass
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


# This is deliberately transparent and editable.  It is applied to every
# posting after source-specific normalization, including postings outside the
# target role so Browse can offer an "all postings" view.
ROLE_RULE_DESCRIPTION = (
    "A posting is in-role when its title contains analyst, analytics, finance, "
    "risk, treasury, pricing, FP&A, business intelligence, investment banking, "
    "or data-science language."
)
ROLE_TERMS = re.compile(
    r"\b(?:analyst|analytics|finance|financial|risk|treasury|pricing|fp&a|"
    r"business intelligence|investment banking|data scientist|data science|"
    r"quantitative)\b",
    re.IGNORECASE,
)


def is_in_role(title: str) -> bool:
    """Return whether *title* matches the project's editable role rule."""

    return bool(ROLE_TERMS.search(title or ""))


SOURCE_BY_ID = {source.id: source for source in SOURCES}

