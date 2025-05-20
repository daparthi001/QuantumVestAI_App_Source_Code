"""
Configuration Settings
Created: 2025-05-20 04:40:55
Author: daparthi001
"""
from pydantic_settings import BaseSettings
from typing import List, Union, Optional
from datetime import datetime
import os

class Settings(BaseSettings):
    # Application Information
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "1.0.0"
    CREATED_DATE: str = "2025-05-20 04:40:55"
    CREATED_BY: str = "daparthi001"
    
    # Environment Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database Configuration
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # Redis Configuration
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # External API Keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    TWITTER_API_SECRET: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Rate Limiting
    RATE_LIMIT_PER_USER: int = 1000
    RATE_LIMIT_PERIOD: int = 3600  # 1 hour
    
    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_PREFIX: str = "quantumvest:"
    
    # Admin Settings
    ADMIN_EMAIL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    
    # Model Settings
    MODEL_CACHE_TTL: int = 3600  # 1 hour
    DEFAULT_FORECAST_DAYS: int = 7
    MAX_FORECAST_DAYS: int = 90
    
    # Feature Flags
    ENABLE_BACKTESTING: bool = True
    ENABLE_REALTIME_UPDATES: bool = True
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def formatted_created_date(self) -> str:
        """Return formatted creation date."""
        return self.CREATED_DATE

# Create settings instance
settings = Settings()