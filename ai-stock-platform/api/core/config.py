"""
Application configuration settings
Created: 2025-05-19 02:59:42 UTC
Author: daparthi001
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import (
    BaseSettings,
    AnyHttpUrl,
    PostgresDsn,
    validator,
    EmailStr,
    Field,
    SecretStr
)
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Application Info
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "1.0.0"
    
    # Pod Info
    POD_NAME: str = Field(default="")
    POD_NAMESPACE: str = Field(default="")
    
    # Environment
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")
    CREATED_AT: str = "2025-05-19 02:59:42"
    CREATED_BY: str = "daparthi001"
    
    # Database Settings
    POSTGRES_SERVER: str = Field(default="")
    POSTGRES_USER: str = Field(default="")
    POSTGRES_PASSWORD: SecretStr = Field(default="")
    POSTGRES_DB: str = Field(default="")
    POSTGRES_PORT: str = Field(default="5432")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)
    DB_POOL_TIMEOUT: int = Field(default=30)

    # Twitter API Credentials
    TWITTER_CONSUMER_KEY: SecretStr = Field(default="")
    TWITTER_CONSUMER_SECRET: SecretStr = Field(default="")
    TWITTER_ACCESS_TOKEN: SecretStr = Field(default="")
    TWITTER_ACCESS_SECRET: SecretStr = Field(default="")

    # Application Secrets
    JWT_SECRET: SecretStr = Field(default="")
    ADMIN_USERNAME: str = Field(default="admin")
    ADMIN_PASSWORD: SecretStr = Field(default="")
    ADMIN_EMAIL: EmailStr = Field(default="admin@example.com")
    ALPHA_VANTAGE_API_KEY: SecretStr = Field(default="")

    # Resource Limits (from K8s)
    CPU_REQUEST: str = Field(default="250m")
    CPU_LIMIT: str = Field(default="1000m")
    MEMORY_REQUEST: str = Field(default="512Mi")
    MEMORY_LIMIT: str = Field(default="1Gi")

    # Storage Paths
    UPLOAD_DIR: str = Field(default="/app/uploads")
    TMP_DIR: str = Field(default="/tmp")

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD").get_secret_value() if values.get("POSTGRES_PASSWORD") else "",
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )

    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Created: 2025-05-19 02:59:42 UTC
    Author: daparthi001
    """
    return Settings()

settings = get_settings()