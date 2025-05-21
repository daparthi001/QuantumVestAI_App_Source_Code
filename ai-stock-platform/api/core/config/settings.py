"""
Settings Module
Created: 2025-05-21 15:20:00
Author: daparthi001
"""
from functools import cached_property
from typing import List, Union
from pydantic import Field, AnyHttpUrl, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    
    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Generate database URI from components"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        """Validate and process CORS origins"""
        if isinstance(value, str):
            if not value.startswith("["):
                return [origin.strip() for origin in value.split(",")]
            return value
        return value

    @field_validator("DB_POOL_SIZE", "DB_MAX_OVERFLOW", "DB_POOL_RECYCLE")
    @classmethod
    def validate_db_settings(cls, value: int, info) -> int:
        """Validate database settings"""
        if value < 0:
            raise ValueError(f"{info.field_name} must be non-negative")
        if info.field_name == "DB_POOL_SIZE" and value < 1:
            raise ValueError("DB_POOL_SIZE must be at least 1")
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True,
        extra="allow"
    )

# Create global settings instance
settings = Settings()

# Export settings
__all__ = ['settings']