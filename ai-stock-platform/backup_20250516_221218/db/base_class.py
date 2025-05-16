"""
SQLAlchemy Base Model Definition
Created: 2025-05-15 21:07:36 (UTC)
Author: daparthi001
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func

# Create a Base class for SQLAlchemy models
Base = declarative_base()

class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamp columns
    to SQLAlchemy models
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())