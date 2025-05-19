"""
Core settings configuration
Created: 2025-05-19 03:25:32
Author: daparthi001
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, PostgresDsn, EmailStr, SecretStr, validator, AnyHttpUrl

class Settings(BaseSettings):
    # Application Info
    VERSION: str = "1.0.0"
    PROJECT_NAME: str = "QuantumVestAI"
    API_V1_STR: str = "/api/v1"
    
    # Pod Information
    POD_NAME: str
    POD_NAMESPACE: str
    
    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    # Twitter API Credentials
    TWITTER_CONSUMER_KEY: SecretStr
    TWITTER_CONSUMER_SECRET: SecretStr
    TWITTER_ACCESS_TOKEN: SecretStr
    TWITTER_ACCESS_SECRET: SecretStr
    
    # Application Secrets
    JWT_SECRET: SecretStr
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: SecretStr
    ADMIN_EMAIL: EmailStr
    ALPHA_VANTAGE_API_KEY: SecretStr
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Resource Settings
    CPU_REQUEST: str = "250m"
    CPU_LIMIT: str = "1000m"
    MEMORY_REQUEST: str = "512Mi"
    MEMORY_LIMIT: str = "1Gi"
    
    # Storage Settings
    UPLOAD_DIR: str = "/app/uploads"
    TMP_DIR: str = "/tmp"

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        password = values.get("POSTGRES_PASSWORD")
        if password is None:
            return None
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=password.get_secret_value(),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}"
        )

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()