"""
Database Session Module
Created: 2025-05-22 05:06:41
Author: daparthi001
Updated: 2025-06-14 21:58:14 by daparthi001
"""
import logging
import time
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
from urllib.parse import quote_plus

# Fix: Import settings from only one place
from core.config.settings import settings

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
            
            # Get database URL with proper password handling
            db_url = settings.get_db_url()
            
            # Create engine with explicit configuration
            engine = create_engine(
                db_url,
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
                result = conn.execute(text("SELECT version()")).scalar()
                logger.info("Database connection successful: %s", result)
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