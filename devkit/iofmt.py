from __future__ import annotations
import json
import sys
from typing import Any, Dict, List, Tuple

class Exit:
    OK = 0
    INVALID_ARGS = 2
    NOT_FOUND = 3
    DEP_MISSING = 10
    PRECONDITION = 20
    EXTERNAL = 30
    FORBIDDEN = 40
    INTERNAL = 50


def envelope(
    command: str,
    status: str,
    exit_code: int,
    data: Dict[str, Any] | None = None,
    errors: List[dict] | None = None,
):
    return {
        "command": command,
        "status": status,
        "exit_code": exit_code,
        "data": data or {},
        "errors": errors or [],
    }


def _format_error(payload: Dict[str, Any]) -> Tuple[str, List[str]]:
    cmd = payload.get("command", "")
    errs = payload.get("errors", []) or []
    if not errs:
        return ("An error occurred.", [f"Run 'devkit {cmd} --help' for usage."] if cmd else [])
    e = errs[0]
    code = e.get("code")
    detail = e.get("detail")

    msg = "An error occurred."
    tips: List[str] = []

    if code == "NOT_FOUND":
        # Service or resource missing
        msg = f"not found: {detail}"
        if cmd.startswith("service"):
            tips.append("List services with 'devkit service list'.")
    elif code == "DUPLICATE":
        msg = f"already exists: {detail}"
    elif code == "BACKUP_MISSING":
        msg = f"backup file not found: {detail}"
        tips.append("Check the path or pass --backup with a valid file.")
    elif code == "DB_NAME_INFER":
        msg = f"could not infer database name: {detail}"
        tips.append("Provide --db-name or ensure Rails config is accessible.")
    elif code == "SAFE_MODE":
        msg = "safe mode is enabled"
        tips.append("Re-run with --yes or unset DEVKIT_SAFE.")
    elif code == "RAILS_CMD":
        msg = f"rails command failed: {detail}"
    elif code == "RESTORE_FAILED":
        msg = "restore failed using pg_restore/psql"
    elif code == "VALIDATE_FAILED":
        msg = f"database validation failed: {detail}"

    if cmd:
        tips.append(f"Run 'devkit {cmd} --help' for usage.")
    return msg, tips


def emit(ctx, payload):
    if ctx.format == "json":
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    else:
        if payload.get("status") == "error":
            msg, tips = _format_error(payload)
            B = "\033[1m"  # bold
            R = "\033[0m"
            sys.stderr.write(f"{B}ERROR:{R} {msg}\n")
            for tip in tips:
                sys.stderr.write(f"{B}TIP:{R} {tip}\n")
    return payload["exit_code"]
