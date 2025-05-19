"""
Configuration Settings
Created: 2025-05-19 05:43:23
Author: daparthi001
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, PostgresDsn, validator, AnyHttpUrl
import os

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration - from RDS credentials secret
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "quantumvest")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    # Twitter API Configuration - from twitter-secrets
    TWITTER_CONSUMER_KEY: str = os.getenv("TWITTER_CONSUMER_KEY", "")
    TWITTER_CONSUMER_SECRET: str = os.getenv("TWITTER_CONSUMER_SECRET", "")
    TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_SECRET: str = os.getenv("TWITTER_ACCESS_SECRET", "")

    # Application Secrets - from app-secrets
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")

    # Pod Information
    POD_NAME: str = os.getenv("POD_NAME", "local")
    POD_NAMESPACE: str = os.getenv("POD_NAMESPACE", "dev")

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT", "5432"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )

    class Config:
        case_sensitive = True

settings = Settings()