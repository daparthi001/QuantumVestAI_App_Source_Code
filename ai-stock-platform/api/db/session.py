"""
Database Session Module
Created: 2025-05-22 04:20:10
Author: daparthi001
"""
import logging
import time
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError

from core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_db_engine(retries: int = 3, delay: int = 5):
    """Create database engine with retry logic"""
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
                settings.SQLALCHEMY_DATABASE_URI,  # Changed from DATABASE_URL
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                connect_args={
                    "connect_timeout": 10,
                    "application_name": f"quantumvestai_{settings.API_ENV}",
                    "sslmode": "require"
                }
            )
            
            # Test connection
            with engine.connect() as conn:
                version = conn.execute("SELECT version()").scalar()
                logger.info("Database connection successful: %s", version)
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
        except Exception as e:
            logger.error("Unexpected error during database connection: %s", str(e))
            raise

# Create database engine
try:
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
        logger.debug("Database connection checked out from pool")

    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_con, connection_record):
        """Log connection returns to pool"""
        logger.debug("Database connection returned to pool")

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except Exception as e:
    logger.error("Failed to initialize database: %s", str(e))
    raise

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Log final configuration
logger.info(
    "Database configuration summary:\n"
    "Host: %s\n"
    "Port: %s\n"
    "Database: %s\n"
    "User: %s\n"
    "Environment: %s\n"
    "SSL Mode: require\n"
    "Pool Size: 5\n"
    "Max Overflow: 10\n"
    "Pool Recycle: 1800s",
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_NAME,
    settings.DB_USER,
    settings.API_ENV
)