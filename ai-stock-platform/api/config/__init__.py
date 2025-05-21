"""
Configuration Module
Created: 2025-05-21 13:43:31
Author: daparthi001
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application Settings"""
    
    # Project Metadata
    PROJECT_NAME: str = os.getenv('PROJECT_NAME', "QuantumVestAI")
    VERSION: str = os.getenv('VERSION', "1.0.0")
    API_V1_STR: str = os.getenv('API_V1_STR', "/api/v1")
    DEBUG: bool = os.getenv('API_ENV', 'development') == 'development'
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', "DEBUG" if DEBUG else "INFO")
    LOG_FORMAT: str = (
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        if DEBUG else
        '{"timestamp":"%(asctime)s","service":"%(name)s",'
        '"level":"%(levelname)s","message":"%(message)s"}'
    )
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:3000"
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# Create settings instance
settings = Settings()

__all__ = ['settings']