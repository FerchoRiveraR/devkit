# Contributing to DevKit

Thanks for your interest in improving DevKit! This guide explains how to set up your environment, make changes safely, and open a clean pull request.

If you’re in a hurry, read AGENTS.md for a concise repository overview and conventions. This doc expands on those details with step‑by‑step instructions.

## Prerequisites
- Python 3.11+
- Recommended: pyenv to manage Python versions
- Recommended: pipx to install Poetry
- Development: Poetry for dependency management
- Optional (DB features): `psql` and `pg_restore` in `PATH`
- Optional (Rails integration): `rails` in `PATH`

## Quick Start
```bash
# Python 3.11 via pyenv
curl https://pyenv.run | bash
pyenv install 3.11.9
pyenv local 3.11.9

# Tools
python3 -m pip install --user pipx
pipx ensurepath
pipx install poetry

# Project setup
make dev
poetry run devkit --help
```

Useful make targets
- `make dev`: install dependencies via Poetry
- `make test`: run pytest quietly
- `make lint`: Ruff lint + format check
- `make fmt`: apply Ruff formatting
- `make docs` / `make docs-serve`: build or serve docs at http://localhost:8000
- `make build`: build the package
- `make install`: install the built package via pipx

Run the CLI during development
```bash
poetry run devkit service list
poetry run devkit db reset myapp --backup /path/to/backup.dump --trace
```

## Development Workflow
1) Create a branch
```bash
git checkout -b feat/<slug>
# or fix/<slug>, docs/<slug>
```
2) Implement changes (see “Code Organization” and “Style & UX”).
3) Keep docs and tests updated as you go.
4) Before pushing:
```bash
make fmt && make lint && make test && make docs
```
5) Open a PR with a clear description, rationale, and screenshots/logs when UX changes.

## Code Organization
- Commands (Typer): `devkit/cli.py` (sub-apps: `service`, `db`, `meta`)
- Domain helpers: `devkit/services.py`, `devkit/postgres.py`, `devkit/rails.py`, `devkit/iofmt.py`
- Introspection: `devkit/introspect.py` and `scripts/generate_reference.py`
- Docs: `docs/*.md` (manual + auto-generated `commands.md`)

Adding or changing commands
- Define parameters and help text in Typer (`devkit/cli.py`).
- Put logic in small, focused helpers under `devkit/*` modules.
- For machine-readable output, build payloads with `iofmt.envelope(...)` and print via `iofmt.emit(...)` when `--format json`.
- Keep command names, flags, and messages consistent with existing commands.

## Style & UX
- Python 3.11+, type hints preferred, small functions.
- Ruff controls formatting and lint (100-char lines).
- Naming: modules snake_case, classes PascalCase, functions/vars snake_case.
- CLI output must be predictable:
  - Support `--format text|json`, `--quiet/--verbose`, `--trace` consistently.
  - Honor safety: `--yes`, `--safe`, and `DEVKIT_SAFE=1` (require confirmations for destructive actions unless explicitly allowed).
  - Use structured error payloads with clear tips when possible.

## Testing
- Framework: pytest. Place tests in `tests/` as `test_*.py` with functions `test_*`.
- Unit tests over integration: mock external tools (Rails, Postgres) and filesystem.
- Keep tests fast; avoid network or invoking real CLIs.
- Useful patterns:
  - Monkeypatch `subprocess.run` and environment variables.
  - Use `tmp_path`/`tmp_path_factory` for filesystem isolation.
  - Provide regression tests for bug fixes.
- Run locally:
```bash
make test
```

## Documentation
- Edit `docs/*.md` when features or flags change.
- Re-generate the command reference after modifying the CLI:
```bash
poetry run python scripts/generate_reference.py > docs/commands.md
```
- Build/serve the docs to verify formatting:
```bash
make docs
make docs-serve  # http://localhost:8000
```

## Commits, Branching, and PRs
- Conventional Commits: `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, etc.
- Branches: `feat/<slug>`, `fix/<slug>`, `docs/<slug>`.
- PR checklist:
  - `make fmt`, `make lint`, `make test`, `make docs` all pass
  - Updated docs and regenerated `docs/commands.md` if CLI changed
  - Clear description, rationale, and screenshots/logs for UX changes

## Security & Safety
- Do not commit secrets. Use environment variables.
- Treat destructive operations carefully; require `--yes` when `--safe`/`DEVKIT_SAFE=1` is active.
- Guard external dependencies (Rails, Postgres) with helpful error messages.

## Reporting Issues & Requesting Enhancements
- Include steps to reproduce, expected vs actual, logs, and environment.
- For enhancements, propose the UX (commands/flags) first to align on design.

## Questions?
Open an issue. Thanks for contributing!
