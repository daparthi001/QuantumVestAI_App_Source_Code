from pydantic_settings import BaseSettings
from typing import List, Union, Optional
import os
from datetime import timedelta

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Twitter API settings
    twitter_consumer_key: Optional[str] = None
    twitter_consumer_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None
	
class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "QuantumVestAI API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    API_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # API Keys for external data sources
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    YAHOO_FINANCE_API_KEY: Optional[str] = None
    
    # Redis (for caching and rate limiting)
    REDIS_URL: Optional[str] = None
    
    # Rate limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"  # Default rate limit
    RATE_LIMIT_AUTH: str = "20/minute"      # Auth endpoints rate limit
    
    # Model settings
    DEFAULT_FORECAST_DAYS: int = 7
    MAX_FORECAST_DAYS: int = 90
    MODEL_CACHE_TTL: int = 3600  # 1 hour
    
    # Feature toggles
    ENABLE_BACKTESTING: bool = True
    ENABLE_REALTIME_UPDATES: bool = True
    ENABLE_SENTIMENT_ANALYSIS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()