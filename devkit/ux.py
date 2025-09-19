from rich.console import Console
from rich.prompt import Confirm

# Disable colors for a simpler look-and-feel
console = Console(no_color=True)


def confirm(prompt: str, default: bool = False) -> bool:
    return Confirm.ask(prompt, default=default)


def table(headers, rows) -> str:
    """Render a simple header + rows listing without borders or colors.

    Returns a plain string suitable for stdout.
    """
    headers = [str(h) for h in headers]
    str_rows = [[str(x) for x in r] for r in rows]
    widths = [len(h) for h in headers]
    for r in str_rows:
        for i, cell in enumerate(r):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
            else:
                widths.append(len(cell))
    lines = []
    header_line = "  ".join(h.upper().ljust(widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    for r in str_rows:
        line = "  ".join((r[i] if i < len(r) else "").ljust(widths[i]) for i in range(len(widths)))
        lines.append(line)
    return "\n".join(lines)
