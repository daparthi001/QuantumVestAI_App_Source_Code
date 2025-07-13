from pydantic import BaseModel


# Simple stub of pydantic-settings for tests
class BaseSettings(BaseModel):
    """Minimal replacement for pydantic_settings.BaseSettings"""

    model_config: dict = {}

SettingsConfigDict = dict


__all__ = ["BaseSettings", "SettingsConfigDict"]
