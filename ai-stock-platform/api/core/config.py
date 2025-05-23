"""
Configuration Module
Created: 2025-05-22 05:06:41
Author: daparthi001
"""
import os
import logging
from typing import Optional
from pydantic import BaseModel, Field, SecretStr, PostgresDsn, validator
from pydantic_settings import BaseSettings
from urllib.parse import quote

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings"""
    # API Information
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env='LOG_LEVEL')
    
    # Database settings
    DB_HOST: str = Field(default="localhost", env='DB_HOST')
    DB_PORT: str = Field(default="5432", env='DB_PORT')
    DB_NAME: str = Field(default="quantumvestaidb", env='DB_NAME')
    DB_USER: str = Field(default="dbadmin", env='DB_USER')
    DB_PASSWORD: Optional[SecretStr] = Field(default=None, env='DB_PASSWORD')
    
    # Environment
    API_ENV: str = Field(default="development", env='API_ENV')
    
    # Security settings
    SECRET_KEY: Optional[str] = Field(default=None, env='SECRET_KEY')
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        # Validate log level
        @classmethod
        def customize_validation(cls, values):
            """Validate and normalize log level"""
            log_level = values.get('LOG_LEVEL', 'INFO').upper()
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            
            if log_level not in valid_levels:
                logger.warning(f"Invalid log level {log_level}. Defaulting to INFO.")
                values['LOG_LEVEL'] = 'INFO'
            return values

    def get_db_url(self) -> str:
        """Get database URL with proper password handling"""
        # Use default values if not set
        host = self.DB_HOST or 'quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com'
        port = self.DB_PORT or '5432'
        name = self.DB_NAME or 'quantumvestaidb'
        user = self.DB_USER or 'dbadmin'
        
        # Handle password
        if not self.DB_PASSWORD:
            password = os.getenv('DB_PASSWORD', '75LerK%0_J<t$H}Z')
        else:
            password = self.DB_PASSWORD.get_secret_value()
        
        # URL encode the password to handle special characters
        encoded_password = quote(password)
        
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=user,
            password=encoded_password,
            host=host,
            port=int(port),
            path=name
        ))

def get_settings() -> Settings:
    """Get settings with validation and logging"""
    try:
        # Create settings instance
        settings = Settings(
            DB_HOST=os.getenv('DB_HOST', 'quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com'),
            DB_PORT=os.getenv('DB_PORT', '5432'),
            DB_NAME=os.getenv('DB_NAME', 'quantumvestaidb'),
            DB_USER=os.getenv('DB_USER', 'dbadmin'),
            DB_PASSWORD=os.getenv('DB_PASSWORD', '75LerK%0_J<t$H}Z'),
            API_ENV=os.getenv('API_ENV', 'development'),
            LOG_LEVEL=os.getenv('LOG_LEVEL', 'INFO')
        )
        
        # Configure logging based on settings
        logging.getLogger().setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        # Log configuration (excluding sensitive information)
        logger.info(
            "Configuration loaded:\n"
            "Host: %s\n"
            "Port: %s\n"
            "Database: %s\n"
            "User: %s\n"
            "Environment: %s\n"
            "Log Level: %s",
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_NAME,
            settings.DB_USER,
            settings.API_ENV,
            settings.LOG_LEVEL
        )
        
        return settings
        
    except Exception as e:
        logger.error("Failed to load settings: %s", str(e))
        # Log environment variables for debugging (excluding sensitive info)
        logger.debug("Environment variables:")
        for key, value in os.environ.items():
            if key.startswith('DB_') and 'PASSWORD' not in key:
                logger.debug("%s: %s", key, value)
        raise

# Create settings instance
settings = get_settings()