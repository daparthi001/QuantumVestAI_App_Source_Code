"""
Settings Module
Created: 2025-05-20 22:13:01
Author: daparthi001
"""
import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings. This class will be automatically populated
    from environment variables and/or .env file.
    """
    # Project Metadata
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8000"]
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_MAX_BYTES: int = 10_000_000  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "quantumvestai"
    POSTGRES_PORT: str = "5432"
    
    # Database Pool Settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Generate database URI from components"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

# Create a global settings instance
settings = Settings()