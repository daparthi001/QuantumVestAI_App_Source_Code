"""Compatibility wrapper for Alembic migrations."""

# Re-export the main application ``User`` model so that existing migration
# scripts referencing ``alembic.db.models.user`` continue to function without
# defining a duplicate table.
from db.models.user import User  # noqa: F401
__all__ = ["User"]