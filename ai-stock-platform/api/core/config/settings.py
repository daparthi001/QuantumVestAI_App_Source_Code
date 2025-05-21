"""
Settings Module
Created: 2025-05-20 21:42:17
Author: daparthi001
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl

class Settings(BaseSettings):
    # Project Metadata
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=True)
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:8000"])
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    LOG_FILE: str = Field(default="logs/app.log")
    LOG_FILE_MAX_BYTES: int = Field(default=10_000_000)  # 10MB
    LOG_FILE_BACKUP_COUNT: int = Field(default=5)
    LOG_DATE_FORMAT: str = Field(default="%Y-%m-%d %H:%M:%S")
    
    # Database Settings
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="")
    POSTGRES_DB: str = Field(default="quantumvestai")
    POSTGRES_PORT: str = Field(default="5432")
    
    # Database Pool Settings
    DB_POOL_SIZE: int = Field(default=5, ge=1)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0)
    DB_POOL_RECYCLE: int = Field(default=3600, ge=0)
    DB_ECHO: bool = Field(default=False)
    
    # Security Settings
    SECRET_KEY: str = Field(default="your-secret-key-here")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    
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
        case_sensitive=True
    )

# Create a global settings instance
settings = Settings()

# Export settings
__all__ = ['settings']