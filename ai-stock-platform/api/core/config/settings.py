"""
Settings Module
Created: 2025-05-20 21:12:19
Author: daparthi001
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "QuantumVestAI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:8000"])
    
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