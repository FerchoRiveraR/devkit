from __future__ import annotations
from .shell import which


def diagnose() -> dict:
    bins = {b: (which(b) or None) for b in ["rails", "psql", "pg_restore"]}
    ok = all(bins.values())
    return {"binaries": bins, "ok": ok}
