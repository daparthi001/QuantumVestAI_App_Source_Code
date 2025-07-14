"""
Configuration Tests
Created: 2025-05-20 04:27:13
Author: daparthi001
"""
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))
sys.path.append(os.path.join(ROOT, "ui"))
import pytest
from api.core.config import Settings, validate_settings


def test_settings_validation():
    """Test settings validation."""
    settings = Settings(
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_password",
        POSTGRES_DB="test_db",
        POSTGRES_PORT="5432",
        JWT_SECRET="test_secret",
        ALPHA_VANTAGE_API_KEY="test_key",
        ADMIN_EMAIL="admin@test.com",
        ADMIN_USERNAME="admin",
        ADMIN_PASSWORD="admin_password",
        TWITTER_API_KEY="twitter_key",
        TWITTER_API_SECRET="twitter_secret",
        NEWS_API_KEY="news_key"
    )
    
    # Validate settings
    assert settings.PROJECT_NAME == "QuantumVestAI"
    assert settings.VERSION == "1.0.0"
    assert settings.CREATED_BY == "daparthi001"
    assert settings.CREATED_DATE == "2025-05-20 04:27:13"
    
    # Test database URL construction
    assert str(settings.SQLALCHEMY_DATABASE_URI).startswith("postgresql://")

def test_cors_origins_validation():
    """Test CORS origins validation."""
    # Test with string input
    settings = Settings(
        BACKEND_CORS_ORIGINS="http://localhost,http://localhost:8080"
    )
    assert len(settings.BACKEND_CORS_ORIGINS) == 2
    
    # Test with list input
    settings = Settings(
        BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:8080"]
    )
    assert len(settings.BACKEND_CORS_ORIGINS) == 2
    
    # Test with invalid input
    with pytest.raises(ValueError):
        Settings(BACKEND_CORS_ORIGINS=123)

def test_environment_validation():
    """Test environment-specific settings."""
    # Test development environment
    settings = Settings(ENVIRONMENT="development")
    assert settings.DEBUG is True
    
    # Test production environment
    settings = Settings(ENVIRONMENT="production")
    assert settings.DEBUG is False


def test_ui_cors_origins_empty_string():
    """Ensure UI settings handle empty CORS_ORIGINS"""
    from ui.config.settings import Settings as UISettings

    settings = UISettings(CORS_ORIGINS="")
    assert settings.CORS_ORIGINS == []
