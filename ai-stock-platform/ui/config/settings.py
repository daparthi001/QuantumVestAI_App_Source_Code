import os
from pydantic import BaseSettings
from pydantic import validator  # validator is still in pydantic
from typing import Optional

class Settings(BaseSettings):
    """Application settings for QuantumVestAI"""
    # Application settings
    APP_NAME: str = "QuantumVestAI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    
    # API settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://quantumvestai-api:5000")
    
    # Authentication settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Yahoo Finance settings
    YAHOO_FINANCE_API_KEY: str = os.getenv("YAHOO_FINANCE_API_KEY", "")
    
    # Twitter API settings
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_SECRET: str = os.getenv("TWITTER_ACCESS_SECRET", "")
    
    # UI settings
    THEME_COLOR: str = os.getenv("THEME_COLOR", "primary")  # primary, dark, light
    ENABLE_ANIMATIONS: bool = os.getenv("ENABLE_ANIMATIONS", "True").lower() in ("true", "1", "t")
    CACHE_DURATION: int = int(os.getenv("CACHE_DURATION", "3600"))  # in seconds
    
    # Database settings - for direct DB access if needed
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_PORT: Optional[int] = int(os.getenv("DB_PORT", "5432"))
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    
    # Security validators
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v, values):
        if values.get("ENVIRONMENT") != "development" and not v:
            raise ValueError("JWT_SECRET_KEY must be set in production")
        return v
    
    @validator("YAHOO_FINANCE_API_KEY")
    def validate_yahoo_api_key(cls, v, values):
        if values.get("ENVIRONMENT") != "development" and not v:
            raise ValueError("YAHOO_FINANCE_API_KEY must be set in production")
        return v

    # Helper methods
    @property
    def is_production(self):
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self):
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_url(self):
        """Dynamically build the database URL if needed"""
        if all([self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]):
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return None

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a settings instance
settings = Settings()