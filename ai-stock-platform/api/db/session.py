"""
Database session configuration.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pathlib import Path

from api.core.config import settings  # Changed to absolute import

# Database URL - update this with your actual database URL
DATABASE_URL = "sqlite:///./test.db"  # For development, replace with your actual database URL

# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
