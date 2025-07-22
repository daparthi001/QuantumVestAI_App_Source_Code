"""
Centralized Application Configuration Settings
This module provides the canonical settings and configuration for all QuantumVestAI services.
"""
from typing import Optional
from pydantic import BaseModel, Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseModel):
    host: str = Field(default="quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com", env='DB_HOST')
    port: str = Field(default="5432", env='DB_PORT')
    name: str = Field(default="quantumvestaidb", env='DB_NAME')
    user: str = Field(default="dbadmin", env='DB_USER')
    password: Optional[SecretStr] = Field(default=None, env='DB_PASSWORD')
    dsn: Optional[PostgresDsn] = None

    def build_dsn(self):
        if not self.dsn:
            self.dsn = f"postgresql://{self.user}:{self.password.get_secret_value() if self.password else ''}@{self.host}:{self.port}/{self.name}"
        return self.dsn

class Settings(BaseSettings):
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=True)
    DB: DatabaseSettings = DatabaseSettings()

settings = Settings()

def get_settings():
    return settings

__all__ = ["settings", "Settings", "get_settings"]
