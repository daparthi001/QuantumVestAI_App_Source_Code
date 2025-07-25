"""
Centralized Application Configuration Settings
This module provides the canonical settings and configuration for all QuantumVestAI services.
"""
from typing import Optional
import os
from pydantic import BaseModel, Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Allow arbitrary extra fields for backwards compatibility
    model_config = SettingsConfigDict(extra="ignore")

    # API base URL used by the UI when calling the backend
    API_BASE_URL: str = Field(default="http://quantumvestai-dev-api:8000", env="API_BASE_URL")

    # Security Settings
    SECRET_KEY: str = Field(default="your-secret-key", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    BACKEND_CORS_ORIGINS: list[str] | str | None = None

    # Toggle demo mode for UI. When False the UI fetches live data.
    DEMO_MODE: bool = Field(default=True, env="DEMO_MODE")

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        return v or []

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.database.get_db_url()

    def get_db_url(self) -> str:
        return self.database.get_db_url()

def get_settings() -> Settings:
    """Return an initialized :class:`Settings` instance.

    The Kubernetes deployment defines an environment variable named ``DATABASE``
    which conflicts with Pydantic's handling of the nested ``database`` model.
    Removing this variable before instantiation prevents JSON decoding errors
    when the settings object is created.
    """

    removed = os.environ.pop("DATABASE", None)
    try:
        return Settings()
    finally:
        if removed is not None:
            os.environ["DATABASE"] = removed


settings = get_settings()

__all__ = ["settings", "Settings", "get_settings"]

