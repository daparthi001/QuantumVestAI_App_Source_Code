"""
Configuration Module
Created: 2025-05-22 05:06:41
Author: daparthi001
"""
import os
import logging
from typing import Optional
from pydantic import BaseSettings, Field, SecretStr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings"""
    # API Information
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    DB_HOST: str = Field(env='DB_HOST')
    DB_PORT: str = Field(default="5432", env='DB_PORT')
    DB_NAME: str = Field(env='DB_NAME')
    DB_USER: str = Field(env='DB_USER')
    DB_PASSWORD: SecretStr = Field(env='DB_PASSWORD')
    
    # Environment
    API_ENV: str = Field(default="development", env='API_ENV')
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def get_db_url(self) -> str:
        """Get database URL with proper password handling"""
        if not self.DB_PASSWORD:
            raise ValueError("Database password is not set")
        
        # Get the raw password string
        password = self.DB_PASSWORD.get_secret_value()
        
        return (
            f"postgresql://{self.DB_USER}:{password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

def get_settings() -> Settings:
    """Get settings with validation"""
    try:
        # Create settings instance
        settings = Settings(
            DB_HOST=os.getenv('DB_HOST', 'quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com'),
            DB_PORT=os.getenv('DB_PORT', '5432'),
            DB_NAME=os.getenv('DB_NAME', 'quantumvestaidb'),
            DB_USER=os.getenv('DB_USER', 'dbadmin'),
            DB_PASSWORD=os.getenv('DB_PASSWORD', '75LerK%0_J<t$H}Z'),
            API_ENV=os.getenv('API_ENV', 'development')
        )
        
        # Log configuration (excluding password)
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