"""
Configuration Module
Created: 2025-05-22 05:06:41
Author: daparthi001
Updated: 2025-06-14 20:28:31 by daparthi001
"""
import logging
import os
from typing import Optional
from urllib.parse import quote

from pydantic import Field, SecretStr, validator

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    # API Information
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
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
    
    # Twitter API settings
    TWITTER_BEARER_TOKEN: Optional[str] = Field(default=None, env='TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY: Optional[str] = Field(default=None, env='TWITTER_API_KEY')
    TWITTER_API_SECRET: Optional[str] = Field(default=None, env='TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN: Optional[str] = Field(default=None, env='TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_SECRET: Optional[str] = Field(default=None, env='TWITTER_ACCESS_SECRET')

    @validator("LOG_LEVEL")
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

    class Config:
        env_file = ".env"
        case_sensitive = True

# Instantiate settings
settings = Settings()

# Set up logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(
    "Configuration loaded: Host=%s, Port=%s, Database=%s, User=%s, Environment=%s, Log Level=%s",
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER,
    settings.API_ENV,
    settings.LOG_LEVEL
)
