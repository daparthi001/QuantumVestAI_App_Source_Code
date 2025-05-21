"""
Configuration Module
Created: 2025-05-21 18:24:40
Author: daparthi001
"""
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator
from pydantic.validators import str_validator

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "QuantumVestAI API"
    DESCRIPTION: str = "AI-Powered Investment Platform API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings from deployment configuration
    DB_HOST: str = "quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com"
    DB_PORT: str = "5432"
    DB_NAME: str = "quantumvestaidb"
    DB_USER: str = "dbadmin"
    DB_PASSWORD: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    # Environment
    API_ENV: str = "development"

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Construct database URI from components"""
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASSWORD"),
            host=values.get("DB_HOST"),
            port=values.get("DB_PORT"),
            path=f"/{values.get('DB_NAME') or ''}"
        )

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()