"""
Application Configuration Settings

This module manages application-wide configuration settings,
providing a centralized way to handle environment-specific 
and application-level configurations.
"""
import os
from typing import Optional
from pydantic import BaseModel, Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseModel):
    """Database configuration settings"""
    host: str = Field(default="quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com", env='DB_HOST')
    port: str = Field(default="5432", env='DB_PORT')
    name: str = Field(default="quantumvestaidb", env='DB_NAME')
    user: str = Field(default="dbadmin", env='DB_USER')
    password: Optional[SecretStr] = Field(default=None, env='DB_PASSWORD')

    def get_db_url(self) -> str:
        """
        Generate database connection URL
        
        Returns:
            str: Fully formed database connection URL
        """
        # Retrieve password, with fallback to default
        db_password = (
            self.password.get_secret_value() if self.password 
            else os.getenv('DB_PASSWORD', '75LerK%0_J<t$H}Z')
        )
        
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=self.user,
            password=db_password,
            host=self.host,
            port=int(self.port),
            path=self.name
        ))

class Settings(BaseSettings):
    """Main application settings"""
    # Project Metadata
    PROJECT_NAME: str = Field(default="QuantumVestAI API", env='PROJECT_NAME')
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = Field(default="1.0.0", env='APP_VERSION')
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    API_ENV: str = Field(default="development", env='API_ENV')
    
    # Database Settings
    database: DatabaseSettings = DatabaseSettings()
    
    # Security Settings
    SECRET_KEY: str = Field(default="your-secret-key", env='SECRET_KEY')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    TWITTER_BEARER_TOKEN: Optional[str] = Field(default=None, env='TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY: Optional[str] = Field(default=None, env='TWITTER_API_KEY')
    TWITTER_API_SECRET: Optional[str] = Field(default=None, env='TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN: Optional[str] = Field(default=None, env='TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = Field(default=None, env='TWITTER_ACCESS_TOKEN_SECRET')
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env='SLACK_WEBHOOK_URL')
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env='LOG_LEVEL')
    
    # Allow extra fields
    model_config = {'extra': 'ignore', 'env_file': '.env', 'case_sensitive': False}
    
    def get_db_url(self) -> str:
        """
        Proxy method to get database URL
        
        Returns:
            str: Database connection URL
        """
        return self.database.get_db_url()

def get_settings() -> Settings:
    """
    Initialize and return application settings
    
    Returns:
        Settings: Configured application settings
    """
    return Settings()

# Global settings instance
settings = get_settings()

# Expose utility function for direct DB URL retrieval
def get_db_url() -> str:
    """
    Retrieve database connection URL
    
    Returns:
        str: Database connection URL
    """
    return settings.get_db_url()