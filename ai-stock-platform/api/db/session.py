"""
Database Session Module
Created: 2025-05-21 20:53:56
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

# Log database connection info (excluding sensitive data)
logger.info(
    "Configuring database connection:\n"
    "Host: %s\n"
    "Port: %s\n"
    "Database: %s\n"
    "User: %s\n"
    "Environment: %s",
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER,
    settings.API_ENV
)

# Database engine configuration
pool_settings = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 1800,
    "pool_pre_ping": True
}

# Create database engine with RDS-optimized settings
engine: Engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    poolclass=QueuePool,
    echo=True,  # Enable SQL logging for debugging
    connect_args={
        "connect_timeout": 10,
        "application_name": f"quantumvestai_{settings.API_ENV}"
    },
    **pool_settings
)

# Add engine event listeners for debugging
@event.listens_for(engine, "connect")
def on_connect(dbapi_con, connection_record):
    """Log new database connections"""
    logger.info("New database connection established")

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

# Log pool configuration
logger.info(
    "Database connection pool configured with:\n"
    "Pool size: %d\n"
    "Max overflow: %d\n"
    "Pool timeout: %d seconds\n"
    "Pool recycle: %d seconds",
    pool_settings["pool_size"],
    pool_settings["max_overflow"],
    pool_settings["pool_timeout"],
    pool_settings["pool_recycle"]
)

# Add connection status check
def check_connection() -> bool:
    """Check database connection status"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error("Database connection test failed: %s", str(e))
        return False

# Verify environment variables are set
required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Perform initial connection test
if not check_connection():
    logger.warning(
        "Initial database connection failed. "
        "The application will continue to retry connections."
    )