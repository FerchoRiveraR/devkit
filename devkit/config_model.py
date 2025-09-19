from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class DbConfig(BaseModel):
    user: str = "postgres"
    host: str = "localhost"
    port: int = 5432
    name: Optional[str] = None

class Service(BaseModel):
    name: str
    app_path: str
    backup_path: str
    env: str = "development"
    db: DbConfig = Field(default_factory=DbConfig)

class Config(BaseModel):
    version: int = 1
    services: List[Service] = Field(default_factory=list)

    @field_validator("services")
    @classmethod
    def unique_names(cls, v: List[Service]):
        names = [s.name for s in v]
        if len(names) != len(set(names)):
            raise ValueError("service names must be unique")
        return v
