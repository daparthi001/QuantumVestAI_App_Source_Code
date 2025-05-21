"""
Configuration Module
Created: 2025-05-21 19:07:45
Author: daparthi001
"""
import os
import logging
from typing import Any, Dict, Optional
from pydantic import BaseSettings, Field, validator

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings with environment variable mapping
    DB_HOST: str = Field(env='DB_HOST')
    DB_PORT: str = Field(env='DB_PORT', default="5432")
    DB_NAME: str = Field(env='DB_NAME')
    DB_USER: str = Field(env='DB_USER')
    DB_PASSWORD: str = Field(env='DB_PASSWORD')
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    # Environment
    API_ENV: str = Field(env='API_ENV', default="development")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

        # Additional environment variable names
        env_prefix = ""
        
        # Allow environment variables to override .env file
        env_priority = True

def get_settings() -> Settings:
    """Get settings instance with logging"""
    try:
        settings = Settings()
        logger.info(
            "Loaded configuration:\n"
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
        return settings
    except Exception as e:
        logger.error("Failed to load configuration: %s", str(e))
        raise

# Create settings instance
settings = get_settings()