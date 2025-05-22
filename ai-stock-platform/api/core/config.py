"""
Configuration Module
Created: 2025-05-22 04:08:10
Author: daparthi001
"""
import os
import logging
from pydantic import BaseSettings, Field

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
    
    # Database settings with explicit environment variable mapping
    DB_HOST: str = Field(
        default=...,  # ... means required
        env='DB_HOST',
        description="Database host address"
    )
    DB_PORT: str = Field(
        default="5432",
        env='DB_PORT',
        description="Database port"
    )
    DB_NAME: str = Field(
        default=...,
        env='DB_NAME',
        description="Database name"
    )
    DB_USER: str = Field(
        default=...,
        env='DB_USER',
        description="Database username"
    )
    DB_PASSWORD: str = Field(
        default=...,
        env='DB_PASSWORD',
        description="Database password"
    )
    
    # Environment
    API_ENV: str = Field(
        default="development",
        env='API_ENV',
        description="API environment (development/production)"
    )

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    """Get settings instance with validation"""
    try:
        # Create settings instance
        settings = Settings()
        
        # Log configuration (excluding sensitive data)
        logger.info(
            "Database configuration loaded:\n"
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
        logger.error("Failed to load settings: %s", str(e))
        # Log environment variables for debugging (excluding password)
        logger.debug("Environment variables:")
        for key, value in os.environ.items():
            if key.startswith('DB_') and 'PASSWORD' not in key:
                logger.debug("%s: %s", key, value)
        raise

# Create settings instance
settings = get_settings()