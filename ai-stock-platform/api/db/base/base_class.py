"""
Database Base Class Module
Created: 2025-05-21 16:32:45
Author: daparthi001
"""
from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for all database models"""
    id: Any
    __name__: str
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically"""
        return cls.__name__.lower()
