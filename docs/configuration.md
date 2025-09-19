# Configuration

DevKit stores configuration in a single YAML file:

- Location: `~/.devkit/config.yml`
- Schema: list of services with app paths, backup paths, and DB settings.

Example:

```yaml
version: 1
services:
  - name: myapp
    app_path: /path/to/rails/app
    backup_path: /path/to/backup.dump
    env: development
    db:
      user: postgres
      host: localhost
      port: 5432
      name: myapp_development
```

Notes
- The file is created automatically on first run (e.g., `devkit service list`).
- `db.name` can be omitted; DevKit will try to infer it from Rails when needed.
- Edit values via commands (`service edit`) or directly in the YAML and re-run.

