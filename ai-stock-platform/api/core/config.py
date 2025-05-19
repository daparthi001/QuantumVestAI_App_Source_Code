"""
Core settings configuration
Created: 2025-05-19 03:42:25
Author: daparthi001
"""
from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl, EmailStr, SecretStr
from typing import Optional, List, Dict, Any
from pathlib import Path

class Settings(BaseSettings):
    # Application metadata
    VERSION: str = "1.0.0"
    PROJECT_NAME: str = "QuantumVestAI"
    CREATED_DATE: str = "2025-05-19 03:42:25"
    AUTHOR: str = "daparthi001"
    
    # API settings
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    # Security settings
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Admin account
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: SecretStr
    ADMIN_EMAIL: EmailStr
    
    # API keys
    ALPHA_VANTAGE_API_KEY: SecretStr
    
    # Redis settings
    REDIS_URL: Optional[str] = None
    REDIS_PREFIX: str = "quantumvest:"
    
    # Storage settings
    UPLOAD_DIR: Path = Path("/app/uploads")
    TEMP_DIR: Path = Path("/tmp")
    
    # External services
    TWITTER_CONSUMER_KEY: SecretStr
    TWITTER_CONSUMER_SECRET: SecretStr
    TWITTER_ACCESS_TOKEN: SecretStr
    TWITTER_ACCESS_SECRET: SecretStr

    class Config:
        case_sensitive = True
        env_file = ".env"

    def get_metadata(self) -> Dict[str, Any]:
        """Get application metadata"""
        return {
            "version": self.VERSION,
            "created_date": self.CREATED_DATE,
            "author": self.AUTHOR,
            "environment": self.ENVIRONMENT
        }

settings = Settings()