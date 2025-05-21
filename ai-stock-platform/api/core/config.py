"""
Configuration Module
Created: 2025-05-21 18:19:56
Author: daparthi001
"""
from typing import Any, Dict, Optional
from pydantic import BaseSettings, PostgresDsn, validator
from pydantic.validators import str_validator

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "Stock Portfolio API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # AWS RDS Database settings
    RDS_HOST: str
    RDS_PORT: str = "5432"
    RDS_DB_NAME: str
    RDS_USERNAME: str
    RDS_PASSWORD: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Construct database URI from RDS components"""
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("RDS_USERNAME"),
            password=values.get("RDS_PASSWORD"),
            host=values.get("RDS_HOST"),
            port=values.get("RDS_PORT"),
            path=f"/{values.get('RDS_DB_NAME') or ''}",
        )

    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()