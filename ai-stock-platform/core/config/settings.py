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

    def get_db_url(self) -> str:
        db_password = self.password.get_secret_value() if self.password else ''
        return f"postgresql://{self.user}:{db_password}@{self.host}:{self.port}/{self.name}"

class Settings(BaseSettings):
    PROJECT_NAME: str = Field(default="QuantumVestAI", env="PROJECT_NAME")
    VERSION: str = Field(default="0.1.0", env="APP_VERSION")
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=True, env="DEBUG")
    database: DatabaseSettings = DatabaseSettings()

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.database.get_db_url()

    def get_db_url(self) -> str:
        return self.database.get_db_url()

settings = Settings()

def get_settings():
    return settings

__all__ = ["settings", "Settings", "get_settings"]
