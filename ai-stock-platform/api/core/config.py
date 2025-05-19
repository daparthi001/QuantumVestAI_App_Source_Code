"""
Application configuration settings
Created: 2025-05-18 16:24:35 UTC
Author: daparthi001
"""
# CHANGE: Removed pydantic_settings import, using standard pydantic
from pydantic import BaseSettings, AnyHttpUrl, PostgresDsn, validator, EmailStr
from typing import Any, Dict, List, Optional, Union
#from pydantic import (
    BaseSettings,
    AnyHttpUrl,
    PostgresDsn,
    validator,
    EmailStr
)
import os
from functools import lru_cache

class Settings(BaseSettings):  # CHANGE: Using pydantic.BaseSettings directly
    # Application Info
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "1.0.0"
    
    # Environment
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"  # Added DEBUG setting
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CREATED_AT: str = "2025-05-19 02:50:53"
    CREATED_BY: str = "daparthi001"
    
    # Security - Read from Kubernetes secrets
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database - Read from Kubernetes secrets
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )
    
    # Redis - Read from Kubernetes secrets
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
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
    Created: 2025-05-19 02:50:53 UTC
    Author: daparthi001
    """
    return Settings()

settings = get_settings()