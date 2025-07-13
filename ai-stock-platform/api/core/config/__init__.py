"""
Application configuration.
"""
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except Exception:  # noqa: BLE001 - fallback for environments without pydantic_settings
    from pydantic import BaseModel

    class BaseSettings(BaseModel):
        class Config:
            extra = "ignore"

    SettingsConfigDict = dict
import os
from functools import lru_cache
from urllib.parse import quote


class Settings(BaseSettings):
    # Database connection details
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "dbname")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DB_USER}:{quote(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    # External API Keys
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    
    # Cache settings
    CACHE_TTL_TRENDING_STOCKS: int = int(os.getenv("CACHE_TTL_TRENDING_STOCKS", "300"))  # 5 minutes
    ENABLE_REAL_DATA: bool = os.getenv("ENABLE_REAL_DATA", "false").lower() == "true"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

def validate_settings(settings_obj: Settings) -> Settings:
    """Dummy settings validation for tests."""
    return settings_obj
