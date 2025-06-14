"""
UI Application Configuration Settings

This module manages UI-specific configuration settings,
providing a centralized way to handle environment-specific 
and UI-level configurations.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Main UI application settings"""
    # Project Metadata
    PROJECT_NAME: str = "QuantumVestAI UI"
    VERSION: str = "1.0.0"
    
    # Environment Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # UI Settings
    THEME_COLOR: str = os.getenv("THEME_COLOR", "primary")
    ENABLE_ANIMATIONS: bool = os.getenv("ENABLE_ANIMATIONS", "True").lower() in ("true", "1", "t")
    CACHE_DURATION: int = int(os.getenv("CACHE_DURATION", "3600"))
    
    # API Connection
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://quantumvestai-api:5000")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # Authentication settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "ui-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def is_production(self):
        """Check if environment is production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self):
        """Check if environment is development"""
        return self.ENVIRONMENT.lower() == "development"

# Global settings instance
settings = Settings()