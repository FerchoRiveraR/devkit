from __future__ import annotations
from pathlib import Path
import yaml
from typing import Optional
from .config_model import Config, Service

CONFIG_PATH = Path.home() / ".devkit" / "config.yml"


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text("version: 1\nservices: []\n")
    data = yaml.safe_load(CONFIG_PATH.read_text()) or {"version": 1, "services": []}
    return Config.model_validate(data)


def save_config(cfg: Config) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    dumped = yaml.safe_dump(cfg.model_dump(mode="python"), sort_keys=False)
    CONFIG_PATH.write_text(dumped)


def find_service(cfg: Config, name: str) -> Optional[Service]:
    for s in cfg.services:
        if s.name == name:
            return s
    return None
