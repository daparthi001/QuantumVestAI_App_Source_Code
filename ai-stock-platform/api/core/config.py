"""
Configuration Module
Created: 2025-05-21 18:56:12
Author: daparthi001
"""
import os
import logging
from typing import Any, Dict, Optional
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
    
    # Database settings - read directly from environment
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct database URI from components"""
        # Log the connection details (excluding password)
        logger.info(
            "Database configuration - Host: %s, Port: %s, DB: %s, User: %s",
            self.DB_HOST,
            self.DB_PORT,
            self.DB_NAME,
            self.DB_USER
        )
        
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Environment
    API_ENV: str = os.getenv("API_ENV", "development")

    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings(
    # Explicitly read from environment variables
    DB_HOST=os.environ["DB_HOST"],
    DB_PORT=os.environ["DB_PORT"],
    DB_NAME=os.environ["DB_NAME"],
    DB_USER=os.environ["DB_USER"],
    DB_PASSWORD=os.environ["DB_PASSWORD"],
)

# Log the configuration (excluding sensitive data)
logger.info("Configuration loaded with database host: %s", settings.DB_HOST)