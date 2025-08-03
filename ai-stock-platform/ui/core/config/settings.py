"""
QuantumVestAI Application Settings
Last Updated: 2025-06-20 05:47:22
Author: daparthi001settings.py
"""
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # Application name and version
    APP_NAME = "QuantumVestAI"
    APP_VERSION = "1.2.3"
    APP_DESCRIPTION = "Advanced AI-driven stock market predictions and analytics"
    
    # Environment settings
    ENV = os.environ.get("ENVIRONMENT", "development")
    DEBUG = ENV != "production"
    
    # Base directories
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    TEMPLATES_DIR = BASE_DIR / "templates"
    STATIC_DIR = BASE_DIR / "static"
    
    # Secret key for session encryption
    # Use the same default value as the API to avoid mismatched JWT secrets
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")
    
    # CORS settings
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://ui-service:3000,http://quantumvestai-dev-api.dev.svc.cluster.local:8000").split(",")
    
    # Base URL for API requests (without trailing slash)
    API_BASE_URL = os.environ.get("API_BASE_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
    
    # JWT settings
    # JWT secret should default to the same key as the API for local development
    JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
    
    # Redis settings
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
    REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
    
    # Database settings
    DB_HOST = os.environ.get("DB_HOST", "db")
    DB_PORT = int(os.environ.get("DB_PORT", "5432"))
    DB_NAME = os.environ.get("DB_NAME", "quantumvestai")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
    
    # Logging settings
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    # Feature flags - Updated to enable all advanced features
    ENABLE_PREMIUM_FEATURES = True
    ENABLE_SOCIAL_LOGIN = os.environ.get("ENABLE_SOCIAL_LOGIN", "true").lower() == "true"
    ENABLE_EXPERIMENTAL = True
    ENABLE_ADVANCED_ANALYTICS = True
    ENABLE_AI_SENTIMENT = True
    ENABLE_PORTFOLIO_OPTIMIZATION = True
    ENABLE_MULTI_FACTOR_ANALYSIS = True
    
    # Email settings
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    EMAIL_FROM = os.environ.get("EMAIL_FROM", "no-reply@quantumvestai.com")
    
    # OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    
    # API rate limiting
    RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW_MINUTES = int(os.environ.get("RATE_LIMIT_WINDOW_MINUTES", "60"))
    
    # Default pagination settings
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Advanced feature settings
    ADVANCED_FEATURES = {
        "ai_sentiment": {
            "enabled": True,
            "requires_premium": True,
            "description": "Real-time analysis of market sentiment using advanced NLP algorithms"
        },
        "multi_factor_analysis": {
            "enabled": True,
            "requires_premium": True,
            "description": "Comprehensive stock analysis using multiple predictive factors"
        },
        "portfolio_optimization": {
            "enabled": True,
            "requires_premium": True,
            "description": "AI-driven portfolio optimization for maximum returns"
        },
        "prediction_interval": {
            "enabled": True,
            "requires_premium": True,
            "description": "Extended prediction intervals up to 12 months"
        },
        "custom_indicators": {
            "enabled": True,
            "requires_premium": True,
            "description": "Create and backtest custom technical indicators"
        }
    }
    
    # Cache settings
    CACHE_TTL_SECONDS = 300  # 5 minutes
    
    def get_database_url(self) -> str:
        """Get database connection string"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def get_redis_url(self) -> str:
        """Get Redis connection string"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENV == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENV == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.ENV == "testing"
        
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.LOG_LEVEL,
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.LOG_LEVEL,
                    "formatter": "standard",
                    "filename": "logs/app.log",
                    "maxBytes": 10485760,  # 10 MB
                    "backupCount": 5,
                    "encoding": "utf8"
                }
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console", "file"] if not self.is_testing() else ["console"]
            }
        }
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled"""
        if feature_name in self.ADVANCED_FEATURES:
            return self.ADVANCED_FEATURES[feature_name]["enabled"]
        return False

@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance.

    Some hosting environments define a ``DATABASE`` variable which Pydantic
    interprets as a JSON representation of our nested ``database`` model.  The
    UI service only expects individual ``DB_*`` variables, so this unexpected
    variable results in ``JSONDecodeError`` when instantiating :class:`Settings`.
    Temporarily removing ``DATABASE`` avoids the parsing error while preserving
    the original environment for any callers that rely on it.
    """

    removed = os.environ.pop("DATABASE", None)
    try:
        return Settings()
    finally:
        if removed is not None:
            os.environ["DATABASE"] = removed


# Instantiate settings for modules that import ``settings`` directly
settings = get_settings()

# DEPRECATED: All config is now in core/config/settings.py
# This file is no longer used and can be deleted.
