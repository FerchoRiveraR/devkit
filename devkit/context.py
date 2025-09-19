from dataclasses import dataclass
from typing import Literal

OutputFormat = Literal["text", "json"]

@dataclass
class Context:
    format: OutputFormat = "text"
    yes: bool = False
    interactive: bool = True
    safe: bool = False
    quiet: bool = False
    verbose: bool = False
    trace: bool = False
