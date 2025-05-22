"""
Configuration Module
Created: 2025-05-22 04:45:11
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
    
    # Database settings with exact values
    DB_HOST: str = Field(
        default="quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com",
        env='DB_HOST'
    )
    DB_PORT: str = Field(default="5432", env='DB_PORT')
    DB_NAME: str = Field(default="quantumvestaidb", env='DB_NAME')
    DB_USER: str = Field(default="dbadmin", env='DB_USER')
    DB_PASSWORD: str = Field(default="75LerK%0_J<t$H}Z", env='DB_PASSWORD')
    
    # Environment
    API_ENV: str = Field(default="development", env='API_ENV')

    class Config:
        case_sensitive = True

# Create settings instance
try:
    settings = Settings()
    
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
    
except Exception as e:
    logger.error("Failed to load settings: %s", str(e))
    raise