"""
Settings Module
Created: 2025-05-20 19:13:15
Author: daparthi001
"""
from typing import List
import os

from pydantic import AnyHttpUrl, Field, field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "QuantumVestAI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DB_HOST: str = Field(
        default_factory=lambda: os.getenv("DB_HOST", os.getenv("POSTGRES_SERVER", "db"))
    )
    DB_USER: str = Field(
        default_factory=lambda: os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres"))
    )
    DB_PASSWORD: str = Field(
        default_factory=lambda: os.getenv("DB_PASSWORD", os.getenv("POSTGRES_PASSWORD", ""))
    )
    DB_NAME: str = Field(
        default_factory=lambda: os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "quantumvestai"))
    )
    DB_PORT: str = Field(
        default_factory=lambda: os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))
    )
    
    # Database pool settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Generate database URI from components"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding='utf-8'
    )
