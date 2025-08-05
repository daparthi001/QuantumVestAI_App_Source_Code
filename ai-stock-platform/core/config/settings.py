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
    VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    CREATED_BY: str = Field(default="daparthi001", env="CREATED_BY")
    CREATED_DATE: str = Field(default="2025-05-20 04:27:13", env="CREATED_DATE")
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=True, env="DEBUG")
    database: DatabaseSettings = DatabaseSettings()
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Admin user defaults
    ADMIN_EMAIL: Optional[str] = Field(default=None, env="ADMIN_EMAIL")
    ADMIN_USERNAME: Optional[str] = Field(default=None, env="ADMIN_USERNAME")
    ADMIN_PASSWORD: Optional[str] = Field(default=None, env="ADMIN_PASSWORD")
    ADMIN_FULL_NAME: str = Field(default="System Administrator", env="ADMIN_FULL_NAME")

    # Allow arbitrary extra fields for backwards compatibility
    model_config = SettingsConfigDict(extra="ignore")

    # API base URL used by the UI when calling the backend
    API_BASE_URL: str = Field(default="http://quantumvestai-dev-api.dev.svc.cluster.local:8000", env="API_BASE_URL")

    # Security Settings
    SECRET_KEY: str = Field(default="your-secret-key", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    BACKEND_CORS_ORIGINS: list[str] | str | None = None

    # UI CORS origins for backwards compatibility
    CORS_ORIGINS: list[str] | str | None = Field(
        default=["http://ui-service:80", "https://app.quantumvestai.com"],
        env="CORS_ORIGINS",
    )


    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        return v or []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Allow comma-separated string or JSON list."""
        if isinstance(v, str):
            if not v:
                return []
            if v.startswith("["):
                try:
                    import json
                    parsed = json.loads(v)
                    return [orig.strip() for orig in parsed if orig.strip()]
                except Exception:
                    return [orig.strip() for orig in v.strip("[]").split(",") if orig.strip()]
            return [orig.strip() for orig in v.split(",") if orig.strip()]
        return v or []

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.database.get_db_url()

    def get_db_url(self) -> str:
        return self.database.get_db_url()

def get_settings() -> Settings:
    """Return an initialized :class:`Settings` instance.

    The Kubernetes deployment defines environment variables named ``DATABASE``
    or ``database`` which conflict with Pydantic's handling of the nested
    ``database`` model. Removing these variables before instantiation prevents
    JSON decoding errors when the settings object is created.
    """

    removed_vars = {
        key: os.environ.pop(key)
        for key in ("DATABASE", "database")
        if key in os.environ
    }
    try:
        return Settings()
    finally:
        os.environ.update(removed_vars)


settings = get_settings()

__all__ = ["settings", "Settings", "get_settings"]

