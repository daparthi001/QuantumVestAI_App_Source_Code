"""
SQLAlchemy base class configuration
Created: 2025-05-18 16:50:32 UTC
Author: daparthi001
"""
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    """
    Base class for SQLAlchemy models
    Created: 2025-05-18 16:50:32 UTC
    Author: daparthi001
    """
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()