# Repository Guidelines

## Project Structure & Modules
- `devkit/`: Python package and CLI commands (Typer + Rich). Key modules: `cli.py`, `services.py`, `postgres.py`, `rails.py`, `iofmt.py`.
- `docs/`: MkDocs site sources; `scripts/generate_reference.py` autogenerates `docs/commands.md`.
- `scripts/`: Utility scripts used by Make targets.
- Top-level: `pyproject.toml` (Poetry, Ruff, scripts), `Makefile`, `README.md`.

## Build, Test, and Dev
- `make dev`: Install dependencies via Poetry.
- `make test`: Run pytest quietly.
- `make lint`: Ruff lint + format check.
- `make fmt`: Apply Ruff formatting.
- `make docs` / `make docs-serve`: Build or serve docs at `http://localhost:8000`.
- `make build`: Build the package; `make install`: Install via `pipx`.
- Run CLI: `poetry run devkit --help` or `poetry run devkit meta reference --format json`.

## Coding Style & Naming
- Python 3.11+. Prefer type hints and small, focused functions.
- Indentation: 4 spaces for Python. Line length: 100 (Ruff).
- Use Ruff for lint/format; fix issues with `make fmt` before PRs.
- Naming: modules `snake_case.py`, classes `PascalCase`, functions/vars `snake_case`.
- Output: keep CLI text predictable; support `--format json` and `--quiet/--verbose` consistently.

## Testing Guidelines
- Framework: pytest. Place tests in `tests/`, name files `test_*.py` and functions `test_*`.
- Favor unit tests around `devkit/*` behaviors; mock external tools (Rails, Postgres).
- Run locally with `make test`. Add regression tests for bug fixes.

## Commit & PR Guidelines
- History currently lacks a convention. Use Conventional Commits (e.g., `feat: add db reset validation`).
- Branches: `feat/<slug>`, `fix/<slug>`, `docs/<slug>`.
- PRs: clear description, rationale, screenshots or logs when UX changes, link issues, checklist: `make lint`, `make test`, `make docs` pass.

## Security & Configuration
- No secrets in code or docs. Prefer env vars. Honor `DEVKIT_SAFE=1` and destructive flags (`--yes`, `--safe`).
- External CLIs (Rails, Postgres) must be present when relevant; guard with helpful errors.
