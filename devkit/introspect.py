from __future__ import annotations
from typing import Any, Dict, List
import typer

# Robust Typer/Click introspection compatible with Typer >=0.12

def typer_reference(app: typer.Typer) -> Dict[str, Any]:
    from typer.main import get_command  # returns Click command tree

    root = get_command(app)
    ref: Dict[str, Any] = {"name": root.name or "devkit", "commands": []}

    def collect(cmd, ancestors: List[str]):
        # Click command params (options/arguments)
        params = []
        for p in getattr(cmd, "params", []) or []:
            names = getattr(p, "opts", None) or getattr(p, "secondary_opts", None) or [
                getattr(p, "human_readable_name", None) or getattr(p, "name", "")
            ]
            params.append(
                {
                    "name": ",".join(names),
                    "param_type": getattr(p, "param_type_name", "param"),
                    "required": bool(getattr(p, "required", False)),
                    "default": getattr(p, "default", None),
                }
            )

        full_name = " ".join(ancestors + [cmd.name]) if ancestors else cmd.name
        ref["commands"].append({
            "name": full_name,
            "help": getattr(cmd, "help", "") or "",
            "params": params,
        })

        # Recurse into subcommands if this is a Click Group
        subcommands = getattr(cmd, "commands", None)
        if isinstance(subcommands, dict):
            for sub in subcommands.values():
                collect(sub, ancestors + [cmd.name])

    # Collect top-level commands/groups
    for c in root.commands.values():
        collect(c, [])

    return ref
