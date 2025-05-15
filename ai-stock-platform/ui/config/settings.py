import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    # Application settings
    APP_NAME: str = "QuantumVestAI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # API settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://quantumvestai-api:5000")
    
    # Authentication settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your_super_secret_key_here")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Yahoo Finance settings
    YAHOO_FINANCE_API_KEY: str = os.getenv("YAHOO_FINANCE_API_KEY", "")
    
    # UI settings
    THEME_COLOR: str = os.getenv("THEME_COLOR", "primary")  # primary, dark, light
    ENABLE_ANIMATIONS: bool = os.getenv("ENABLE_ANIMATIONS", "True").lower() in ("true", "1", "t")
    CACHE_DURATION: int = int(os.getenv("CACHE_DURATION", "3600"))  # in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()