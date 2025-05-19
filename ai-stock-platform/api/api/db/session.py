"""
Database Session Management
Created: 2025-05-19 05:43:23
Author: daparthi001
"""
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
import backoff

from api.core.config import settings

logger = logging.getLogger(__name__)

def create_engine_with_retry():
    """Create database engine with retry logic for RDS"""
    @backoff.on_exception(
        backoff.expo,
        OperationalError,
        max_tries=5,
        max_time=30
    )
    def _create_engine():
        return create_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=300,  # Recycle connections every 5 minutes
            connect_args={
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5
            }
        )
    
    return _create_engine()

# Create engine instance
engine = create_engine_with_retry()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Get database session with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        db.close()