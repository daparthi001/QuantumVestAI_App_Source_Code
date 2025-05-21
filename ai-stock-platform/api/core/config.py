"""
Configuration Module
Created: 2025-05-21 21:24:47
Author: daparthi001
"""
import os
import logging
from pydantic import BaseSettings, Field, SecretStr

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
    # Use SecretStr for password
    DB_PASSWORD: SecretStr = Field(env='DB_PASSWORD')
    
    # Environment
    API_ENV: str = Field(env='API_ENV', default="development")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct database URI with proper password handling"""
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

def get_settings() -> Settings:
    """Get settings instance with logging"""
    try:
        settings = Settings()
        # Log configuration (excluding password)
        logger.info(
            "Database configuration loaded:\n"
            "Host: %s\n"
            "Port: %s\n"
            "Database: %s\n"
            "User: %s\n"
            "Password: %s\n"
            "Environment: %s",
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_NAME,
            settings.DB_USER,
            "********" if settings.DB_PASSWORD else "NOT SET",
            settings.API_ENV
        )
        return settings
    except Exception as e:
        logger.error("Failed to load settings: %s", str(e))
        raise

# Create settings instance
settings = get_settings()