"""
Core Settings Module
Created: 2025-05-20 18:08:37
Author: daparthi001
"""
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "QuantumVestAI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Add other settings as needed
    class Config:
        env_file = ".env"
        case_sensitive = True