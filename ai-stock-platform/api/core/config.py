"""
Core Configuration
Created: 2025-05-19 04:05:44
Author: daparthi001
"""
from pydantic_settings import BaseSettings
from pydantic import SecretStr, PostgresDsn
from typing import Optional, List
import os

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "QuantumVestAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Market Data API
    ALPHA_VANTAGE_API_KEY: SecretStr
    
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()