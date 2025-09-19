# DevKit

A lightweight CLI for common developer workflows around Rails + Postgres, with a gh-like UX and automation-friendly commands.

## Summary
- Manage multiple Rails apps and their Postgres backups via the `service` command group.
- Reset and restore databases safely with `db reset` using `pg_restore` or `psql`.
- Introspect the CLI programmatically via `meta reference` to power agents/LLMs.

## How to Install
DevKit requires Python 3.11+.

- pyenv (recommended for local Python):
  - Install: `curl https://pyenv.run | bash` (see pyenv docs)
  - Install Python: `pyenv install 3.11.9 && pyenv local 3.11.9`
- pipx (recommended to install devkit as an isolated app):
  - Install: `python3 -m pip install --user pipx && pipx ensurepath`
  - Install devkit: `pipx install .` (from repo root)
- poetry (for development):
  - Install: `pipx install poetry`
  - Setup env: `make dev` then run `poetry run devkit --help`

You can also link the executable wrapper: `make link` (installs `~/.local/bin/devkit`).

## Requirements
- Python 3.11+
- Optional for db features: `psql` and `pg_restore` in `PATH`
- Optional for Rails apps: `rails` in `PATH` to infer DB names

## Contributing
- See `CONTRIBUTING.md` for the full contributor guide.
- Read `AGENTS.md` for repository-wide guidelines (structure, style, tests, commits, PRs).
- Start here (dev setup):
  - Python 3.11+ ready (pyenv recommended): `pyenv install 3.11.9 && pyenv local 3.11.9`
  - Install Poetry: `pipx install poetry`
  - Bootstrap deps: `make dev`
  - Run CLI locally: `poetry run devkit --help`
- Day-to-day commands:
  - Lint/format check: `make lint` (use `make fmt` to apply fixes)
  - Tests: `make test` (pytest; keep fast and focused)
  - Docs build/serve: `make docs` / `make docs-serve`
  - Regenerate command reference: `poetry run python scripts/generate_reference.py > docs/commands.md`
- Code style & expectations:
  - Python 3.11+, type hints preferred, small focused functions.
  - Ruff enforces formatting and a 100-char line length.
  - Output should be predictable; support `--format json`, `--quiet/--verbose`, `--trace` consistently.
  - Honor safety flags in destructive paths: `--yes`, `--safe`, and `DEVKIT_SAFE=1`.
- Adding or changing commands:
  - Typer entry points live in `devkit/cli.py` (sub-apps: `service`, `db`, `meta`).
  - Put domain logic in small helpers (`devkit/services.py`, `devkit/postgres.py`, `devkit/rails.py`, etc.).
  - For machine-friendly output, use `iofmt.envelope(...)` and `iofmt.emit(...)` when `--format json`.
  - Keep UX consistent with existing commands and error messages.
- Tests:
  - Add unit tests under `tests/` (`test_*.py`).
  - Mock external CLIs (Rails, Postgres) and filesystem where appropriate.
  - Add regression tests for bug fixes; keep `make test` fast.
- Docs:
  - Update `docs/*.md` when UX/flags change; add examples for new commands.
  - Rebuild the auto-generated reference after CLI changes: `scripts/generate_reference.py` → `docs/commands.md`.
- Branches, commits, PRs:
  - Branch naming: `feat/<slug>`, `fix/<slug>`, `docs/<slug>`.
  - Conventional Commits (e.g., `feat: add db reset validation`).
  - PR checklist: `make fmt`, `make lint`, `make test`, `make docs` all pass; include rationale and, if UX changed, screenshots/logs.
- Manual testing tips:
  - Use `poetry run devkit ...` with `--trace` to see executed commands.
  - For database flows, ensure `psql`/`pg_restore` are in `PATH`; export `PGPASSWORD` to avoid prompts.
  - See examples in [docs/services.md](./docs/services.md) and [docs/database.md](./docs/database.md).
- Reporting issues & ideas:
  - Open an issue with steps to reproduce, expected vs actual, logs, and environment.
  - For enhancements, propose UX/flags first to align on design before implementation.

## Documentation
- Manual (Markdown only) is under `docs/`:
  - Overview: [docs/index.md](./docs/index.md)
  - Installation: [docs/install.md](./docs/install.md)
  - Configuration: [docs/configuration.md](./docs/configuration.md)
  - Services: [docs/services.md](./docs/services.md)
  - Database: [docs/database.md](./docs/database.md)
  - Command Reference (auto-generated): [docs/commands.md](./docs/commands.md)
  - Agents & Automation: [docs/agents.md](./docs/agents.md)
  - Troubleshooting: [docs/troubleshooting.md](./docs/troubleshooting.md)
