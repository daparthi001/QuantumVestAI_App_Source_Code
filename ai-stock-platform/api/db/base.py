"""
Database Base Module
Created: 2025-05-19 05:45:27
Author: daparthi001
"""
from api.db.base_class import Base, TimestampMixin
from api.db.models.user import User

# Import all models here
# This allows Alembic to detect all models when generating migrations
__all__ = ["Base", "TimestampMixin", "User"]