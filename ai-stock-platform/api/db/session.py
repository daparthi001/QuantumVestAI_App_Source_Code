"""
Database Session Module
Created: 2025-05-21 18:56:12
Author: daparthi001
"""
import os
import logging
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Log all environment variables (excluding sensitive ones)
logger.info("Environment variables for database connection:")
logger.info("DB_HOST: %s", os.environ.get("DB_HOST"))
logger.info("DB_PORT: %s", os.environ.get("DB_PORT"))
logger.info("DB_NAME: %s", os.environ.get("DB_NAME"))
logger.info("DB_USER: %s", os.environ.get("DB_USER"))

# Create database URL directly
database_url = settings.SQLALCHEMY_DATABASE_URI

logger.info("Connecting to database at: %s", database_url.replace(settings.DB_PASSWORD, "********"))

# Create database engine with RDS-optimized settings
engine: Engine = create_engine(
    database_url,
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

# Add engine event listeners for debugging
@event.listens_for(engine, "connect")
def on_connect(dbapi_con, connection_record):
    logger.info("New database connection established")

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_con, connection_record, connection_proxy):
    logger.info("Database connection checked out from pool")

@event.listens_for(engine, "checkin")
def on_checkin(dbapi_con, connection_record):
    logger.info("Database connection returned to pool")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Verify engine configuration
logger.info(
    "Database engine configured with:\n"
    "Pool size: %d\n"
    "Max overflow: %d\n"
    "Pool timeout: %d\n"
    "Pool recycle: %d",
    engine.pool.size(),
    engine.pool.overflow(),
    engine.pool.timeout(),
    engine.pool.recycle()
)