from __future__ import annotations
from pathlib import Path
import os
import subprocess
from typing import List
import yaml


def rails_bin(app_path: Path) -> List[str]:
    bin_rails = app_path / "bin" / "rails"
    return [str(bin_rails)] if bin_rails.exists() else ["rails"]


def infer_db_name(app_path: Path, env: str) -> str:
    # Try 1: parse config/database.yml (may contain ERB; fallback to runner)
    db_yml = app_path / "config" / "database.yml"
    if db_yml.exists():
        try:
            data = yaml.safe_load(db_yml.read_text())
            if env in data and isinstance(data[env], dict) and "database" in data[env]:
                return str(data[env]["database"])
        except Exception:
            pass
    # Try 2: rails runner (supports ERB, credentials)
    cmd = rails_bin(app_path) + ["runner", "puts ActiveRecord::Base.connection_db_config.database"]
    envp = os.environ.copy(); envp["RAILS_ENV"] = env
    res = subprocess.run(cmd, cwd=app_path, env=envp, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0 and res.stdout.strip():
        return res.stdout.strip()
    raise RuntimeError("Could not infer database name")
