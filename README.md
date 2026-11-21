# FDA Job Watcher

![Tests](https://github.com/OWNER/REPOSITORY/actions/workflows/tests.yml/badge.svg)

FDA Job Watcher is a daily, public job-market tracker for the Financial Data Analytics project. It watches public applicant-tracking-system JSON endpoints, saves compressed raw snapshots, rebuilds a deterministic posting history, and publishes a browser-calculated three-page site.

## Current project choices

- **Role rule:** a title matches when it contains analyst, analytics, finance, financial, risk, treasury, pricing, FP&A, business intelligence, investment banking, data scientist, data science, or quantitative language. The rule lives in `jobwatcher/config.py`.
- **Watch list:** 15 employers across Greenhouse and Ashby. The source ID, employer, ATS, and endpoint are all visible in `jobwatcher/config.py`; the normalizer also retains a tested Lever adapter for future replacements.
- **Raw data:** `data/raw/YYYY-MM-DD/<source>.json.gz`. A failed source writes no raw file; its failure is recorded in `_status.json`.
- **Canonical history:** `data/processed/history.json` (descriptions remain in compressed raw evidence so the browser file stays small).
- **Run status:** `data/processed/status.json`.
- **Published site data:** `site/data/history.json` and `site/data/status.json`.

## Run locally

From the repository root:

```text
uv sync --extra dev
uv run pytest
uv run python -m jobwatcher.pipeline --date 2026-11-20
```

The pipeline calls every enabled source, continues after individual failures, writes raw snapshots, rebuilds history from raw files alone, updates the two processed files, and writes the daily issue body to `data/processed/issue.md`.

To preview the site, serve the `site` directory with any static HTTP server. The site has a built-in demo fallback when opened directly from disk, but a local server is needed to test the service worker and published JSON files.

## Site pages

- **Today:** latest run time, source health, open/new/removed counts, and daily changes.
- **Browse:** role/all toggle, employer/location/age filters, title search, sorting, apply links, and browser-local favorites.
- **Market:** six calculations from history: new per day, removed per day, open postings by employer, median days open, removed within seven days, and top open locations.

The site includes a manifest and service worker. Data requests are network-first and fall back to the last cached copy when offline.

## GitHub setup

1. Create a public repository and set `OWNER/REPOSITORY` in the README badge.
2. Enable GitHub Pages with the `pages.yml` workflow.
3. Push the repository to GitHub. `tests.yml` runs pytest on every push.
4. `pipeline.yml` runs daily at 06:00 UTC. It commits raw/history/status artifacts, closes prior open issues, and creates one dated issue with new and removed postings.

The source endpoints are intentionally configuration-driven. Before the first graded run, verify each endpoint returns JSON without login and replace any employer that has changed ATS providers or blocks the request.

