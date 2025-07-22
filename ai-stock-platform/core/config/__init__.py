"""Configuration compatibility layer ."""

from .settings import Settings, get_settings, settings


def validate_settings(cfg: Settings) -> None:
    """Simple validation helper used in tests."""
    cfg.SQLALCHEMY_DATABASE_URI


__all__ = ["settings", "Settings", "get_settings", "validate_settings"]
