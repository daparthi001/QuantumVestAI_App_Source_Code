"""
Database session handling
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from functools import lru_cache

from api.core.config import settings

@lru_cache()
def create_engine_instance():
    return create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        pool_size=32,
        max_overflow=64,
        echo=settings.SQL_ECHO
    )

@lru_cache()
def create_session_factory():
    engine = create_engine_instance()
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    SessionLocal = create_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
