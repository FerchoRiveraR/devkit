from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple
from .shell import run, which


def choose_restore_tool(backup_path: Path) -> Tuple[str, list[str]]:
    name = backup_path.name.lower()
    if name.endswith(".dump") or name.endswith(".backup") or name.endswith(".custom"):
        tool = which("pg_restore") or "pg_restore"
        return tool, ["-1"]
    tool = which("psql") or "psql"
    return tool, ["-f", str(backup_path)]


def validate_connection(
    user: str,
    host: str,
    port: int,
    db: str,
    trace: bool = False,
    env: Optional[dict] = None,
) -> int:
    tool = which("psql") or "psql"
    return run(
        [tool, "-U", user, "-h", host, "-p", str(port), "-d", db, "-c", "SELECT 1;"],
        trace=trace,
        env=env,
    )
