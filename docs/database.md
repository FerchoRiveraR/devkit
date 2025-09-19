# Database

Reset and restore a Postgres database for a configured service.

See also: [services.md](./services.md), [configuration.md](./configuration.md), and [commands.md](./commands.md)

Basic restore from backup
```bash
devkit db reset myapp --backup /path/to/backup.dump
```

Options
- `--env`: Rails environment (defaults to the service `env`)
- `--db-name`: override database name (DevKit will try to infer from Rails if not provided)
- `--yes`: auto-confirm destructive actions (honors `--safe` / `DEVKIT_SAFE=1`)
- `--trace`: show executed commands

How it works
1) Drops and recreates the database via Rails tasks (`db:drop`, `db:create`).
2) Restores using `pg_restore` for custom dumps or `psql -f` for SQL files.
3) Validates connectivity with `SELECT 1`.

Requirements
- `psql`, `pg_restore` in PATH for restore/validate steps.
- `rails` in PATH if DevKit needs to infer the DB name.

Passwords
- DevKit will prompt once for the Postgres password (if needed) and reuse it for all steps.
- To avoid prompts, export `PGPASSWORD` in your environment before running: `export PGPASSWORD=...`.
