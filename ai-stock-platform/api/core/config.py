"""
Configuration Module
Created: 2025-05-21 18:44:09
Author: daparthi001
"""
import os
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings from environment variables
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "quantumvestaidb")
    DB_USER: str = os.getenv("DB_USER", "dbadmin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Construct database URI from components"""
        if isinstance(v, str):
            return v
        
        # Log the connection details (excluding password)
        print(f"Connecting to database at {values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')} as {values.get('DB_USER')}")
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME') or ''}"
        )

    # Environment
    API_ENV: str = os.getenv("API_ENV", "development")

    class Config:
        case_sensitive = True

settings = Settings()