# Services

Manage Rails apps and their database backups.

See also: [configuration.md](./configuration.md) and [commands.md](./commands.md)

List services
```bash
devkit service list
```

Add a service
```bash
devkit service add \
  --name myapp \
  --app /path/to/rails/app \
  --backup /path/to/backup.dump \
  --env development \
  --db-user postgres --db-host localhost --db-port 5432
```

Edit a service
```bash
devkit service edit myapp --env production --db-user appuser
```

Remove a service
```bash
devkit service rm myapp -y
```

Tips
- Use `--format json` for machine-readable output.
- Use `--interactive/--no-interactive` to control prompts and `--yes` for confirmations.
