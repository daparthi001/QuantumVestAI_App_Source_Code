"""
Base Model Implementation
Created: 2025-05-19 03:44:39
Author: daparthi001
"""
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from datetime import datetime
from db.base import Base

class TimestampMixin:
    """Mixin for timestamp columns"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

class UserMixin:
    """Mixin for user-related columns"""
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)

class ModelBase(Base):
    """Base model class"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name"""
        return cls.__name__.lower()
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create model from dictionary"""
        return cls(**{
            key: value
            for key, value in data.items()
            if hasattr(cls, key)        })
