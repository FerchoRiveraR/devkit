# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DevKit is a Python CLI tool for daily development routines (Rails + Postgres), designed with a GitHub-like UX and documentation friendly for agents/LLMs. It manages Rails applications and their database workflows with structured JSON output for automation.

## Development Commands

**Setup:**
```bash
poetry install          # Install dependencies
```

**Testing and Quality:**
```bash
pytest -q              # Run tests
ruff check devkit       # Lint code
ruff format devkit      # Format code
ruff format --check devkit  # Check formatting
```

**Build and Install:**
```bash
poetry build            # Build package
pipx install .          # Install locally
```

**Documentation:**
```bash
python scripts/generate_reference.py > docs/commands.md  # Generate command reference
mkdocs build            # Build documentation
mkdocs serve -a localhost:8000  # Serve docs locally
```

## Architecture

### Core Components

- **CLI Entry Point**: `devkit/cli.py` - Main Typer application with three sub-commands:
  - `service` - Manage Rails app services and their configurations
  - `db` - Database operations (reset, restore from backups)
  - `meta` - Introspection/metadata commands for agents

- **Configuration**: `devkit/config_model.py` + `devkit/services.py`
  - Config stored in `~/.devkit/config.yml`
  - Services define Rails app paths, backup locations, DB connection details
  - Uses Pydantic models for validation

- **Rails Integration**: `devkit/rails.py`
  - Detects Rails binary (rails/bin/rails)
  - Infers database names from Rails configuration

- **Database Operations**: `devkit/postgres.py`
  - Supports both pg_restore and psql for backups
  - Auto-detects backup format and chooses appropriate tool

### Key Modules

- `context.py` - Global context for CLI options (format, verbosity, etc.)
- `iofmt.py` - JSON envelope format for structured output
- `ux.py` - Rich console utilities for tables and confirmations
- `shell.py` - Command execution utilities
- `doctor.py` - System diagnostics
- `introspect.py` - CLI metadata generation for agents

### Agent Integration

For LLM/agent integration, use:
- `devkit meta reference --format json` - Get complete CLI structure
- `devkit meta describe --format json` - Get command descriptions
- Use `--format json --no-interactive --yes` for deterministic execution

Exit codes follow standard conventions (0=success, 1=error, etc.)

## Configuration

Services are managed through the CLI and stored in YAML format at `~/.devkit/config.yml`. Each service includes:
- Rails application path
- Database backup path
- Environment (development/production/etc.)
- Database connection details (user, host, port)

## Dependencies

- **Runtime**: typer, rich, PyYAML, pydantic
- **Development**: pytest, ruff, mkdocs, mkdocs-material
- **Python**: 3.11+
- **External tools**: Rails, PostgreSQL client tools (psql, pg_restore)