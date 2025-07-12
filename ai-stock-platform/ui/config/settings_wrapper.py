"""
Settings Wrapper Module
Created: 2025-06-15 03:25:13
Author: daparthi001
"""
import logging
import os
from typing import Any, Dict, List, Optional

# Try to import settings from different possible locations
            # Create fallback settings if all imports fail
            logger = logging.getLogger(__name__)
            logger.error("Failed to import settings, using fallback settings")
            
            class FallbackSettings:
                def __init__(self):
                    # Default values for critical settings
                    self.API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.quantumvestai.com")
                    self.CORS_ORIGINS = ["http://localhost:3000", "https://app.quantumvestai.com", "*"]
                    self.CORS_ALLOW_CREDENTIALS = True
                    self.CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
                    self.CORS_ALLOW_HEADERS = ["Authorization", "Content-Type"]
                    self.DB_HOST = os.environ.get("DB_HOST", "localhost")
                    self.DB_PORT = os.environ.get("DB_PORT", "5432")
                    self.DB_NAME = os.environ.get("DB_NAME", "quantumvestaidb")
                    self.DB_USER = os.environ.get("DB_USER", "dbadmin")
                    self._DB_PASSWORD = os.environ.get("DB_PASSWORD", "75LerK%0_J<t$H}Z")
                    self.API_ENV = os.environ.get("API_ENV", "development")
                    self.SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
                    self.JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
                    self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
                
                def get_db_url(self):
                    return f"postgresql://{self.DB_USER}:{self._DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                
                def __getattr__(self, name):
                    # Return a default value for any missing attribute
                    logger.warning(f"Accessing undefined setting: {name}, returning default value")
                    if name.startswith('CORS_'):
                        return "*"
                    if name.endswith('_URL'):
                        return "https://example.com"
                    if name.endswith('_KEY'):
                        return "default_key"
                    return ""
            
            settings = FallbackSettings()

# Wrap settings to handle missing attributes
class SettingsWrapper:
    def __init__(self, settings_obj):
        self._settings = settings_obj
    
    def __getattr__(self, name):
        # Check if the attribute exists in the original settings
        if hasattr(self._settings, name):
            return getattr(self._settings, name)
        
        # Provide default values for common settings
        logger.warning(f"Missing setting: {name}, using default value")
        
        # CORS defaults
        if name == 'CORS_ORIGINS':
            return ["http://localhost:3000", "https://app.quantumvestai.com", "*"]
        if name == 'CORS_ALLOW_CREDENTIALS':
            return True
        if name == 'CORS_ALLOW_METHODS':
            return ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        if name == 'CORS_ALLOW_HEADERS':
            return ["Authorization", "Content-Type"]
        
        # API URL defaults
        if name == 'API_BASE_URL':
            return os.environ.get("API_BASE_URL", "https://api.quantumvestai.com")
        
        # Database defaults
        if name == 'DB_HOST':
            return os.environ.get("DB_HOST", "localhost")
        if name == 'DB_PORT':
            return os.environ.get("DB_PORT", "5432")
        if name == 'DB_NAME':
            return os.environ.get("DB_NAME", "quantumvestaidb")
        if name == 'DB_USER':
            return os.environ.get("DB_USER", "dbadmin")
        if name == 'DB_PASSWORD':
            # Simulate SecretStr behavior
            password = os.environ.get("DB_PASSWORD", "75LerK%0_J<t$H}Z")
            return type('SecretStr', (), {'get_secret_value': lambda self: password})()
        
        # Security defaults
        if name == 'SECRET_KEY':
            return os.environ.get("SECRET_KEY", "supersecretkey")
        if name == 'JWT_ALGORITHM':
            return os.environ.get("JWT_ALGORITHM", "HS256")
        if name == 'ACCESS_TOKEN_EXPIRE_MINUTES':
            return int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Fallback for any other setting
        return ""

# Create wrapped settings instance
wrapped_settings = SettingsWrapper(settings)

def get_settings():
    """Get wrapped settings instance"""
    return wrapped_settings
