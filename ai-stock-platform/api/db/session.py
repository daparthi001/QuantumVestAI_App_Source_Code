"""
Database Session Module
Created: 2025-05-20 19:13:15
Author: daparthi001
"""
import logging
from typing import Generator
import backoff
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings

logger = logging.getLogger(__name__)

# Configure backoff parameters
MAX_TRIES = 5
MAX_TIME = 120

@backoff.on_exception(
    backoff.expo,
    (OperationalError, SQLAlchemyError),
    max_tries=MAX_TRIES,
    max_time=MAX_TIME
)
def create_db_engine():
    """Create database engine with retry logic"""
    return create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE,
        echo=settings.DB_ECHO
    )

try:
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logger.critical(f"Failed to initialize database: {str(e)}")
    raise

def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()