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
        test_url = os.getenv("TEST_DATABASE_URL")
        if test_url:
            return test_url
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
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_SECRET: SecretStr = Field(
        default_factory=lambda: os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "your-secret-key"))
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    
    # External Services
    TWITTER_BEARER_TOKEN: Optional[str] = Field(default=None, env='TWITTER_BEARER_TOKEN')
    TWITTER_API_KEY: Optional[str] = Field(default=None, env='TWITTER_API_KEY')
    TWITTER_API_SECRET: Optional[str] = Field(default=None, env='TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN: Optional[str] = Field(default=None, env='TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET: Optional[str] = Field(default=None, env='TWITTER_ACCESS_TOKEN_SECRET')
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env='SLACK_WEBHOOK_URL')

    # Stock Market Data
    # Read the Alpha Vantage API key from the environment. No demo default is
    # provided so missing configuration results in a clear error.
    ALPHA_VANTAGE_API_KEY: Optional[str] = Field(default=None, env='ALPHA_VANTAGE_API_KEY')

    # Cache settings
    CACHE_TTL_TRENDING_STOCKS: int = Field(default=300, env='CACHE_TTL_TRENDING_STOCKS')
    # Default to False so real API calls are only made when explicitly enabled
    ENABLE_REAL_DATA: bool = Field(default=False, env='ENABLE_REAL_DATA')

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env='LOG_LEVEL')

    # Toggle demo mode for the UI. When False the UI fetches live data.
    DEMO_MODE: bool = Field(default=False, env="DEMO_MODE")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Compatibility alias used by older code and tests."""
        return self.get_db_url()
    
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
    """Return an initialized :class:`Settings` instance.

    The hosting environment may define an environment variable named
    ``DATABASE`` which conflicts with Pydantic's handling of the nested
    ``database`` model.  Temporarily removing this variable prevents JSON
    decoding errors during instantiation.
    """

    removed = os.environ.pop("DATABASE", None)
    try:
        return Settings()
    finally:
        if removed is not None:
            os.environ["DATABASE"] = removed

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
