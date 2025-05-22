"""
Configuration Module
Created: 2025-05-21 21:41:33
Author: daparthi001
"""
import os
import logging
from typing import Optional
from pydantic import BaseSettings, validator

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    # Environment
    API_ENV: str = "development"

    @validator("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD", pre=True)
    def validate_db_settings(cls, v: Optional[str], field: str) -> str:
        """Validate database settings"""
        if not v:
            env_val = os.getenv(field.name)
            if not env_val:
                raise ValueError(f"{field.name} must be provided")
            return env_val
        return v

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct database URI"""
        if not all([self.DB_HOST, self.DB_PORT, self.DB_NAME, self.DB_USER, self.DB_PASSWORD]):
            raise ValueError("Database configuration is incomplete")
        
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        case_sensitive = True
        env_prefix = ""

# Create settings instance
settings = Settings(
    DB_HOST=os.getenv("DB_HOST"),
    DB_PORT=os.getenv("DB_PORT", "5432"),
    DB_NAME=os.getenv("DB_NAME"),
    DB_USER=os.getenv("DB_USER"),
    DB_PASSWORD=os.getenv("DB_PASSWORD"),
    API_ENV=os.getenv("API_ENV", "development")
)

# Log configuration (excluding sensitive data)
logger.info(
    "Configuration loaded:\n"
    "Host: %s\n"
    "Port: %s\n"
    "Database: %s\n"
    "User: %s\n"
    "Environment: %s",
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER,
    settings.API_ENV
)

# Verify database configuration
if not all([
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER,
    settings.DB_PASSWORD
]):
    missing_vars = [
        var for var, val in {
            "DB_HOST": settings.DB_HOST,
            "DB_PORT": settings.DB_PORT,
            "DB_NAME": settings.DB_NAME,
            "DB_USER": settings.DB_USER,
            "DB_PASSWORD": settings.DB_PASSWORD
        }.items() if not val
    ]
    raise ValueError(f"Missing required database configuration: {', '.join(missing_vars)}")