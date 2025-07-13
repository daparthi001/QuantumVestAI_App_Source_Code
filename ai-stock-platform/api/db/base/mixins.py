"""
Database Mixins Module
Created: 2025-05-21 16:32:45
Author: daparthi001
"""
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class TimestampMixin:
    """Mixin for adding timestamp columns to models"""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
