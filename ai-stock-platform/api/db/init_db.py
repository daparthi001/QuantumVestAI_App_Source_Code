"""
Database Initialization Module
Created: 2025-05-21 18:44:09
Author: daparthi001
"""
import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError

from db.base import Base
from db.session import engine, SessionLocal
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Initialize database schema with simple retry logic"""
    max_retries = 5
    retry_delay = 4
    current_try = 1

    while current_try <= max_retries:
        try:
            logger.info(
                "Attempting database connection (attempt %d/%d) to %s:%s/%s",
                current_try,
                max_retries,
                settings.DB_HOST,
                settings.DB_PORT,
                settings.DB_NAME
            )
            
            # Try to create database tables
            Base.metadata.create_all(bind=engine)
            logger.info("Successfully created database tables")
            
            # Verify connection
            result = db.execute("SELECT 1").scalar()
            logger.info("Database connection verified: %s", result)
            return
            
        except OperationalError as e:
            logger.error(
                "Database connection failed (attempt %d/%d): %s",
                current_try,
                max_retries,
                str(e)
            )
            
        except ProgrammingError as e:
            logger.error(
                "Database schema error (attempt %d/%d): %s",
                current_try,
                max_retries,
                str(e)
            )
            
        except Exception as e:
            logger.error(
                "Unexpected error (attempt %d/%d): %s",
                current_try,
                max_retries,
                str(e)
            )

        if current_try < max_retries:
            logger.info("Waiting %d seconds before retrying...", retry_delay)
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
        
        current_try += 1
    
    error_msg = f"Failed to initialize database after {max_retries} attempts"
    logger.error(error_msg)
    raise Exception(error_msg)

def main() -> None:
    """Main initialization function"""
    logger.info("Starting database initialization")
    init_db(db=SessionLocal())
    logger.info("Database initialization completed")

if __name__ == "__main__":
    main()