from __future__ import annotations
import subprocess, shlex, os
from pathlib import Path
from typing import List, Optional


def run(cmd: List[str], cwd: Optional[Path]=None, env: Optional[dict]=None, trace: bool=False) -> int:
    if trace:
        print(f"$ {shlex.join(cmd)}")
    p = subprocess.run(cmd, cwd=cwd, env=env or os.environ.copy())
    return p.returncode


def check(cmd: List[str], cwd: Optional[Path]=None, env: Optional[dict]=None, trace: bool=False):
    rc = run(cmd, cwd=cwd, env=env, trace=trace)
    if rc != 0:
        raise RuntimeError(f"Command failed ({rc}): {shlex.join(cmd)}")


def which(bin_name: str) -> Optional[str]:
    from shutil import which as _which
    return _which(bin_name)
