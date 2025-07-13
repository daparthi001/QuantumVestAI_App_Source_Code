"""
Database Mixins Module
Created: 2025-05-21 15:48:25
Author: daparthi001
"""
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class TimestampMixin:
    """Mixin for adding created_at and updated_at columns"""
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
