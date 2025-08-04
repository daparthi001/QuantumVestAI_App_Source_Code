"""
Configuration Settings Module
Created: 2025-05-22 05:06:41
Author: daparthi001
Updated: 2025-06-15 03:16:55 by daparthi001

(DEPRECATED: All config is now in core/config/settings.py)
This file is no longer used and can be deleted.
"""
import logging
from typing import List, Optional, Union
from urllib.parse import quote

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    # API Information
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # API URLs
    API_BASE_URL: str = Field(
        default="https://api.quantumvestai.com",
        env='API_BASE_URL'
    )
    
    # CORS settings
    CORS_ORIGINS: List[str] | str = Field(
        default=["http://ui-service:80", "https://app.quantumvestai.com"],
        env='CORS_ORIGINS'
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Allow comma-separated or JSON list and handle empty values."""
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
        return v

    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env='CORS_ALLOW_CREDENTIALS')
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        env='CORS_ALLOW_METHODS'
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["Authorization", "Content-Type"],
        env='CORS_ALLOW_HEADERS'
    )
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env='LOG_LEVEL')
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env='LOG_FORMAT')
    LOG_DATE_FORMAT: str = Field(default="%Y-%m-%d %H:%M:%S", env='LOG_DATE_FORMAT')
    LOG_FILE: str = Field(default="logs/app.log", env='LOG_FILE')
    LOG_FILE_MAX_BYTES: int = Field(default=10 * 1024 * 1024, env='LOG_FILE_MAX_BYTES')  # 10 MB
    LOG_FILE_BACKUP_COUNT: int = Field(default=5, env='LOG_FILE_BACKUP_COUNT')
    
    # Database settings
    DB_HOST: str = Field(default="db", env='DB_HOST')
    DB_PORT: str = Field(default="5432", env='DB_PORT')
    DB_NAME: str = Field(default="quantumvestaidb", env='DB_NAME')
    DB_USER: str = Field(default="dbadmin", env='DB_USER')
    DB_PASSWORD: Optional[SecretStr] = Field(default=None, env='DB_PASSWORD')
    
    # Environment
    API_ENV: str = Field(default="development", env='API_ENV')
    
    # Security settings
    SECRET_KEY: Optional[str] = Field(default=None, env='SECRET_KEY')
    JWT_ALGORITHM: str = Field(default="HS256", env='JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env='ACCESS_TOKEN_EXPIRE_MINUTES')

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v = v.upper()
        if v not in valid_levels:
            logging.warning(f"Invalid log level {v}. Defaulting to INFO.")
            return "INFO"
        return v

    def get_db_url(self) -> str:
        """Get database URL with proper password handling and encoding"""
        host = self.DB_HOST
        port = self.DB_PORT
        name = self.DB_NAME
        user = self.DB_USER
        password = self.DB_PASSWORD.get_secret_value() if self.DB_PASSWORD else "75LerK%0_J<t$H}Z"
        encoded_password = quote(password)
        return f"postgresql://{user}:{encoded_password}@{host}:{port}/{name}"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

# Set up logging
try:
    log_level = Settings().LOG_LEVEL
except Exception:
    log_level = "INFO"
logging.basicConfig(
    level=getattr(logging, log_level.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_settings():
    """Get a fresh settings instance (for testability)"""
    return Settings()
