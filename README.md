# FDA Job Watcher

![Tests](https://github.com/golmsted2/Job-Watcher-/actions/workflows/tests.yml/badge.svg)

FDA Job Watcher is a daily, public job-market tracker for the Financial Data Analytics project. It watches public applicant-tracking-system JSON endpoints, saves compressed raw snapshots, rebuilds a deterministic posting history, and publishes a browser-calculated finance job site.

## Current project choices

- **Role rule:** US finance only, targeted to recent graduates and early-career candidates. A title must contain finance-specific language and an entry-level signal such as analyst, associate, coordinator, specialist, assistant, rotational, new graduate, or entry-level. Senior/manager/director titles and roles requiring three or more years are excluded. Generic data analyst, analytics, and business-intelligence titles do not match. The rule lives in `jobwatcher/config.py`.
- **Geography rule:** the website only displays explicit US locations or locations with a US state/DC marker. Ambiguous `Remote` postings are excluded unless the source says US/United States.
- **Watch list:** 15 major finance employers: Edward Jones, Stifel, JPMorgan Chase, Bank of America, Citi, Wells Fargo, Goldman Sachs, Morgan Stanley, PNC, U.S. Bank, State Street, BNY, American Express, Capital One, and Northern Trust. JPMorgan and Chase are tracked together because they use the same JPMorgan Chase careers feed. The source ID, employer, ATS, and endpoint are all visible in `jobwatcher/config.py`.
- **Raw data:** `data/raw/YYYY-MM-DD/<source>.json.gz`. A failed source writes no raw file; its failure is recorded in `_status.json`.
- **Assignment history:** `data/history.csv` follows the project handout's fixed column contract. The browser-oriented copy is `data/processed/history.json`.
- **Assignment status:** `data/status.json` follows the handout's compact key names. The browser-oriented copy is `data/processed/status.json`.
- **Published site data:** `site/data/history.json` and `site/data/status.json`.
- **Candidate signals:** salary ranges (including ranges embedded in published ATS descriptions), annualized salary values, work model, internship/new-grad signals, sponsorship language, degree language, freshness, match score, and a normalized duplicate key are derived during normalization.
- **Assignment compliance:** the scheduled pipeline reads the public ATS JSON feeds only; it does not read employer job-board HTML. Salary values remain available when the source JSON or its published description provides them.
- **Privacy:** favorites, application status, and private notes stay in the browser's local storage; they are not committed to the repository or sent to the site.
- **Portable workspace:** saved searches, profile skills, resume text, application deadlines, and analytics can be exported/imported as a local JSON backup. This is the static-site substitute for cross-device accounts until a server-side identity and database are added.

## Board and aggregator sources

The current 15 ATS sources remain the reliable employer-level baseline. They use public JSON feeds behind the employers' career pages:

| Employer | ATS |
| --- | --- |
| Edward Jones | MCloud |
| Stifel | Jibe |
| JPMorgan Chase | Oracle Recruiting Cloud |
| Bank of America | Workday |
| Citi | Eightfold |
| Wells Fargo | Workday |
| Goldman Sachs | Oracle Recruiting Cloud |
| Morgan Stanley | Eightfold |
| PNC | Phenom |
| U.S. Bank | Phenom |
| State Street | Phenom |
| BNY | Oracle Recruiting Cloud |
| American Express | Oracle Recruiting Cloud |
| Capital One | Workday |
| Northern Trust | Workday |

The pipeline also supports optional US job-board APIs for later expansion:

- **Adzuna:** set `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.
- **Jooble:** set `JOOBLE_API_KEY` for the US Jooble API.
- **USAJOBS:** set `USAJOBS_EMAIL` and `USAJOBS_API_KEY`.

Add those values as GitHub Actions repository secrets; the pipeline automatically adds the corresponding sources when their secrets exist. LinkedIn and Indeed are not scraped because their official integrations require approved partner/API access rather than anonymous public job-search JSON endpoints.

## Run locally

From the repository root:

```text
uv sync --extra dev
uv run pytest
uv run python -m jobwatcher.pipeline --date 2026-11-20
```

The pipeline calls every enabled source, continues after individual failures, writes raw snapshots, rebuilds both history contracts from raw files alone, updates the processed and published copies, and writes the daily issue body to `data/processed/issue.md`.

To preview the site, serve the `site` directory with any static HTTP server. The site has a built-in demo fallback when opened directly from disk, but a local server is needed to test the service worker and published JSON files.

After changing the role rule, rebuild the existing raw evidence without refetching employers:

```text
uv run python -m jobwatcher.pipeline --build-only
```

Optional email alerts use the Resend API. Add `RESEND_API_KEY`, `ALERT_EMAIL` (one or more comma-separated recipients), and `ALERT_FROM_EMAIL` as GitHub Actions repository secrets. The daily workflow remains a no-op for email until all three values are present.

## Site pages

- **Today:** latest run time, source health, open/new/removed counts, and daily changes.
- **Browse:** role/all toggle, employer/location/age filters, work model, new-grad/internship stage, program type, sponsorship, degree, salary, application status, title search, sorting, apply links, profile matching, match scores, freshness, duplicate suppression, saved searches, and browser-local application tracking.
- **Role details:** dedicated job pages with source excerpts, salary annualization, cost bands, candidate signals, deadlines, notes, favorites, and direct employer application links.
- **Compare:** select up to three roles and compare salary, fit, profile match, location, program type, cost band, and freshness.
- **Companies:** a profile view for all 15 tracked employers, current open-match counts, feed type, early-career counts, and links into company-filtered roles.
- **Workspace:** application analytics, upcoming deadlines, saved-search new-match counts, resume-text skill matching, location insights, browser alert permission, and manual export/import.
- **Market:** six calculations from all history: new per day with an in-role comparison series, removed per day, open postings by employer, median days open, removed within seven days, and top open locations. The interactive salary explorer is an additional view.

The site includes a manifest and service worker. Data requests are network-first and fall back to the last cached copy when offline.

## GitHub setup

1. Create a public repository and set `OWNER/REPOSITORY` in the README badge.
2. Enable GitHub Pages with the `pages.yml` workflow.
3. Push the repository to GitHub. `tests.yml` runs pytest on every push.
4. `pipeline.yml` runs daily at 06:00 UTC. It commits raw/history/status artifacts, closes prior open issues, and creates one dated issue with new and removed postings.

## File inventory

- `jobwatcher/config.py` — employer watch list, ATS endpoints, and the title/location role rules.
- `jobwatcher/pipeline.py` — JSON source fetching, compressed snapshots, and output orchestration.
- `jobwatcher/normalize.py` — ATS-to-common-column conversion and candidate signals.
- `jobwatcher/history.py` — deterministic history replay, assignment CSV/status exports, and issue text.
- `jobwatcher/alerts.py` — optional Resend email alerts.
- `tests/` — pytest coverage for adapters, title/location rules, history replay, failures, and exports.
- `.github/workflows/tests.yml` — tests on every push and pull request.
- `.github/workflows/pipeline.yml` — daily collection, issue creation, and artifact commit.
- `data/raw/` — compressed dated source evidence and per-day source status.
- `data/history.csv` and `data/status.json` — fixed-path assignment outputs.
- `data/processed/` — browser-oriented history, status, issue body, and derived cache.
- `site/` — GitHub Pages HTML, CSS, JavaScript, manifest, service worker, data copies, and image assets.

The source endpoints are intentionally configuration-driven. Before the first graded run, verify each endpoint returns JSON without login and replace any employer that has changed ATS providers or blocks the request.

