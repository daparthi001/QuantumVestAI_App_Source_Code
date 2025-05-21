"""
Database Initialization Module
Created: 2025-05-21 18:24:40
Author: daparthi001
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    before_log,
    after_log,
    retry_if_exception_type
)

from db.base import Base
from db.session import engine, SessionLocal
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((OperationalError, ProgrammingError)),
    before=before_log(logger, logging.INFO),
    after=before_log(logger, logging.INFO)
)
def init_db(db: Session) -> None:
    """Initialize database schema with retry logic"""
    try:
        # Try to create database tables
        Base.metadata.create_all(bind=engine)
        logger.info(
            "Successfully connected to RDS database at %s (%s environment)",
            settings.DB_HOST,
            settings.API_ENV
        )
        
        # Verify connection
        db.execute("SELECT 1")
        logger.info("Database connection verified")
        
    except OperationalError as e:
        logger.error(
            "Failed to connect to RDS database at %s: %s",
            settings.DB_HOST,
            str(e)
        )
        raise
        
    except ProgrammingError as e:
        logger.error(
            "Database schema error at %s: %s",
            settings.DB_HOST,
            str(e)
        )
        raise
        
    except Exception as e:
        logger.error(
            "Unexpected error during database initialization: %s",
            str(e)
        )
        raise

def main() -> None:
    """Main initialization function"""
    logger.info(
        "Initializing database connection to RDS at %s (%s environment)",
        settings.DB_HOST,
        settings.API_ENV
    )
    init_db(db=SessionLocal())
    logger.info("Database initialization completed")

if __name__ == "__main__":
    main()