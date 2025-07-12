"""
Database Base Package
Created: 2025-05-21 16:32:45
Author: daparthi001
"""
from .base_class import Base
from .mixins import TimestampMixin

__all__ = ["Base", "TimestampMixin"]
