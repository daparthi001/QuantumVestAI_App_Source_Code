"""
Database Base Module
Created: 2025-05-21 14:28:57
Author: daparthi001
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

class CustomBase:
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name"""
        return cls.__name__.lower()
    
    # Common columns that should be in all tables
    id: int
    created_at: str
    updated_at: str
    
    def dict(self):
        """Convert model instance to dictionary"""
        return {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns
        }

# Create declarative base model
Base = declarative_base(cls=CustomBase)