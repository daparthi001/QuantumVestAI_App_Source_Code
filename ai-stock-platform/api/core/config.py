"""
Configuration Module
Created: 2025-05-22 05:06:41
Author: daparthi001
"""
import logging
from typing import Optional
from pydantic import Field, SecretStr, validator
from pydantic_settings import BaseSettings
from urllib.parse import quote

class Settings(BaseSettings):
    """Application settings"""
    # API Information
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env='LOG_LEVEL')
    
    # Database settings
    DB_HOST: str = Field(default="localhost", env='DB_HOST')
    DB_PORT: str = Field(default="5432", env='DB_PORT')
    DB_NAME: str = Field(default="quantumvestaidb", env='DB_NAME')
    DB_USER: str = Field(default="dbadmin", env='DB_USER')
    DB_PASSWORD: Optional[SecretStr] = Field(default=None, env='DB_PASSWORD')
    
    # Environment
    API_ENV: str = Field(default="development", env='API_ENV')
    
    # Security settings
    SECRET_KEY: Optional[str] = Field(default=None, env='SECRET_KEY')

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