"""Minimal stub for the :mod:`pydantic_settings` package used in tests."""

try:  # pragma: no cover - prefer the real package if available
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
except Exception:  # pragma: no cover - fallback implementation
    from pydantic import BaseModel

    class BaseSettings(BaseModel):
        class Config:
            extra = "ignore"

    SettingsConfigDict = dict

__all__ = ["BaseSettings", "SettingsConfigDict"]
