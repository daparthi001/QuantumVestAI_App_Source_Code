"""
Configuration Settings Module for QuantumVestAI
Created: 2025-05-19 03:44:39
Updated: 2025-06-15 03:42:15
Author: daparthi001
"""
import os
import logging
from pathlib import Path
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, validator

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Application settings"""
    # Project information
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered Investment Platform"
    
    # Environment settings
    ENVIRONMENT: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=3000, env="PORT")
    
    # API settings
    API_BASE_URL: str = Field(default="https://api.quantumvestai.com", env="API_BASE_URL")
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "https://app.quantumvestai.com", "*"],
        env="CORS_ORIGINS"
    )
    
    # Static files and templates
    STATIC_DIR: str = Field(default=str(BASE_DIR / "static"), env="STATIC_DIR")
    TEMPLATES_DIR: str = Field(default=str(BASE_DIR / "templates"), env="TEMPLATES_DIR")
    UPLOAD_DIR: str = Field(default=str(BASE_DIR / "uploads"), env="UPLOAD_DIR")
    
    # Database settings
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: str = Field(default="5432", env="DB_PORT")
    DB_NAME: str = Field(default="quantumvestaidb", env="DB_NAME")
    DB_USER: str = Field(default="dbadmin", env="DB_USER")
    DB_PASSWORD: Optional[SecretStr] = Field(default=None, env="DB_PASSWORD")
    
    # Security settings
    SECRET_KEY: str = Field(
        default="supersecretkey123456789abcdef",
        env="SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_FILE: Optional[str] = Field(default="logs/app.log", env="LOG_FILE")
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in valid_levels:
            logging.warning(f"Invalid log level {v}. Defaulting to INFO.")
            return "INFO"
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    def get_db_url(self) -> str:
        """Get database URL with proper password handling"""
        password = ""
        if self.DB_PASSWORD:
            password = self.DB_PASSWORD.get_secret_value()
        else:
            password = os.environ.get("DB_PASSWORD", "")
        
        return f"postgresql://{self.DB_USER}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

# Configure basic logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Log settings for debugging
logger.info(
    "Settings loaded - Environment: %s, Debug: %s, Host: %s, Port: %s",
    settings.ENVIRONMENT,
    settings.DEBUG,
    settings.HOST,
    settings.PORT
)

def get_settings():
    """Return settings instance"""
    return settings