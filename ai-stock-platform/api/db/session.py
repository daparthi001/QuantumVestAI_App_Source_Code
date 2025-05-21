"""
Database Session Module
Created: 2025-05-21 18:24:40
Author: daparthi001
"""
from typing import Generator
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with RDS-optimized settings
engine: Engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    poolclass=QueuePool,
    pool_size=5,  # Start with smaller pool for dev environment
    max_overflow=10,  # Allow up to 15 total connections
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "application_name": f"quantumvestai_{settings.API_ENV}"  # Identify application in RDS logs
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