"""
Core settings configuration
Created: 2025-05-19 03:11:17
Author: daparthi001
"""
from pydantic import BaseSettings, PostgresDsn
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    VERSION: str = "1.0.0"  # Added VERSION attribute
    PROJECT_NAME: str = "QuantumVestAI"
    DEBUG: bool = False
    
    # Database settings
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    class Config:
        case_sensitive = True

settings = Settings()