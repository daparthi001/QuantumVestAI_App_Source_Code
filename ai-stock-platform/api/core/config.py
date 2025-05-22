"""
Configuration Module
Created: 2025-05-22 04:42:10
Author: daparthi001
"""
import os
import logging
from pydantic import BaseSettings, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DB_HOST: str = Field(..., env='DB_HOST')
    DB_PORT: str = Field(default="5432", env='DB_PORT')
    DB_NAME: str = Field(..., env='DB_NAME')
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASSWORD: str = Field(..., env='DB_PASSWORD')
    
    # Environment
    API_ENV: str = Field(default="development", env='API_ENV')

    @validator("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    def validate_not_empty(cls, v, field):
        """Validate that fields are not empty"""
        if not v:
            raise ValueError(f"{field.name} cannot be empty")
        return v

    class Config:
        case_sensitive = True

# Create settings instance
try:
    settings = Settings()
    
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
    
except Exception as e:
    logger.error("Failed to load settings: %s", str(e))
    raise