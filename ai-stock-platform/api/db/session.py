"""
Database Session Module
Created: 2025-05-21 21:24:47
Author: daparthi001
"""
import os
import logging
import time
from typing import Generator, Optional
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
import urllib.parse

from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def verify_credentials() -> bool:
    """Verify that all database credentials are present"""
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error("Missing required environment variables: %s", ', '.join(missing_vars))
        return False
    
    if not settings.DB_PASSWORD or not settings.DB_PASSWORD.get_secret_value():
        logger.error("Database password is not set or is empty")
        return False
    
    return True

def create_db_engine(retries: int = 3, delay: int = 5) -> Optional[Engine]:
    """
    Create database engine with retry logic
    
    Args:
        retries: Number of connection retries
        delay: Delay between retries in seconds
    
    Returns:
        SQLAlchemy Engine instance or None if all retries fail
    """
    # Verify credentials before attempting connection
    if not verify_credentials():
        raise ValueError("Database credentials verification failed")

    # Create the connection URL with properly escaped password
    password = urllib.parse.quote_plus(settings.DB_PASSWORD.get_secret_value())
    db_url = (
        f"postgresql+psycopg2://{settings.DB_USER}:{password}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    
    for attempt in range(retries):
        try:
            logger.info(
                "Attempting database connection (attempt %d/%d) to %s:%s",
                attempt + 1,
                retries,
                settings.DB_HOST,
                settings.DB_PORT
            )
            
            # Create engine with explicit configuration
            engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                echo=True,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": f"quantumvestai_{settings.API_ENV}",
                    "sslmode": "require"  # Enable SSL for RDS
                }
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
                logger.info("Database connection successful")
                return engine
                
        except OperationalError as e:
            logger.error(
                "Database connection attempt %d/%d failed: %s",
                attempt + 1,
                retries,
                str(e)
            )
            if attempt < retries - 1:
                logger.info("Retrying in %d seconds...", delay)
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error("All connection attempts failed")
                raise
    
    return None

# Create database engine
engine = create_db_engine()
if not engine:
    raise RuntimeError("Failed to create database engine")

# Add engine event listeners for debugging
@event.listens_for(engine, "connect")
def on_connect(dbapi_con, connection_record):
    """Log new database connections"""
    logger.info("New database connection established")
    # Set session parameters
    dbapi_con.set_session(
        application_name=f"quantumvestai_{settings.API_ENV}"
    )

@event.listens_for(engine, "checkout")
def on_checkout(dbapi_con, connection_record, connection_proxy):
    """Log connection checkouts from pool"""
    logger.info("Database connection checked out from pool")

@event.listens_for(engine, "checkin")
def on_checkin(dbapi_con, connection_record):
    """Log connection returns to pool"""
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

# Log final configuration (excluding sensitive data)
logger.info(
    "Database configuration summary:\n"
    "Host: %s\n"
    "Port: %s\n"
    "Database: %s\n"
    "User: %s\n"
    "Environment: %s\n"
    "SSL Mode: require",
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER,
    settings.API_ENV
)