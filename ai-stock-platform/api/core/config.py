"""
Configuration Module
Created: 2025-05-21 21:12:20
Author: daparthi001
"""
import os
import logging
from pydantic import BaseSettings, Field

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
    
    # Environment
    API_ENV: str = Field(env='API_ENV', default="development")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Construct database URI"""
        # Explicitly use postgresql+psycopg2 driver
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
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
        # Log all environment variables for debugging
        logger.info("Environment variables:")
        for key, value in os.environ.items():
            if key.startswith('DB_'):
                if 'PASSWORD' in key:
                    logger.info("%s: %s", key, '*' * 8)
                else:
                    logger.info("%s: %s", key, value)
        
        # Log the constructed database URL (without password)
        db_url = settings.SQLALCHEMY_DATABASE_URI
        masked_url = db_url.replace(settings.DB_PASSWORD, "********")
        logger.info("Database URL: %s", masked_url)
        
        return settings
    except Exception as e:
        logger.error("Failed to load settings: %s", str(e))
        raise

# Create settings instance
settings = get_settings()