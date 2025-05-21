"""
Database Session Module
Created: 2025-05-21 18:44:09
Author: daparthi001
"""
import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log database connection details (excluding password)
logger.info(
    "Configuring database connection to %s:%s/%s as %s",
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER
)

# Create database engine with RDS-optimized settings
engine: Engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=True,  # Enable SQL logging for debugging
    connect_args={
        "connect_timeout": 10,
        "application_name": f"quantumvestai_{settings.API_ENV}"
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()