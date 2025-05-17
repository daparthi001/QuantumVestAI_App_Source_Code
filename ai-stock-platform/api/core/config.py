"""
Application configuration settings.
Created: 2025-05-17 14:49:00
Author: daparthi001
"""
from typing import Any, Dict, List, Optional, Union
from pydantic import (
    AnyHttpUrl,
    PostgresDsn,
    field_validator
)
from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    CREATED_AT: str = "2025-05-17 14:56:36"
    CREATED_BY: str = "daparthi001"
    
    # Security - Read from Kubernetes secrets
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database - Read from Kubernetes secrets
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode='before')
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )
    
    # Redis - Read from Kubernetes secrets
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str]
    
    # AWS - Using IAM roles, no credentials needed
    S3_BUCKET: str = os.getenv("S3_BUCKET", "quantumvest-files")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Created: 2025-05-17 14:56:36 UTC
    Author: daparthi001
    """
    return Settings()

settings = get_settings()