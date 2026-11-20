# FDA Job Watcher

- Run Python from this repository root with `uv run python ...`.
- Run tests with `uv run pytest`.
- Raw source snapshots belong under `data/raw/YYYY-MM-DD/`.
- The canonical history and run status belong under `data/processed/`.
- The static site reads the published copies under `site/data/`.
- Keep source adapters in `jobwatcher/` and add tests for every normalization rule.

