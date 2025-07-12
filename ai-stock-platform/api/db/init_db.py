"""
Database Initialization Module
Created: 2025-05-21 18:56:12
Author: daparthi001
"""
import os
import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, ProgrammingError
import socket

from db.base import Base
from db.session import engine, SessionLocal
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_db_connection() -> tuple[bool, str]:
    """
    Check if database is reachable
    Returns: (is_reachable, message)
    """
    try:
        # Try to establish a TCP connection
        sock = socket.create_connection(
            (settings.DB_HOST, int(settings.DB_PORT)),
            timeout=5
        )
        sock.close()
        return True, "Database is reachable"
    except Exception as e:
        return False, f"Cannot reach database: {str(e)}"

def init_db(db: Session) -> None:
    """Initialize database schema with diagnostics"""
    max_retries = 5
    retry_delay = 4
    current_try = 1

    # Print environment for debugging
    logger.info("Database connection environment:")
    logger.info("DB_HOST: %s", os.environ.get("DB_HOST"))
    logger.info("DB_PORT: %s", os.environ.get("DB_PORT"))
    logger.info("DB_NAME: %s", os.environ.get("DB_NAME"))
    logger.info("DB_USER: %s", os.environ.get("DB_USER"))
    
    while current_try <= max_retries:
        logger.info(
            "Attempt %d/%d - Connecting to database at %s:%s",
            current_try,
            max_retries,
            settings.DB_HOST,
            settings.DB_PORT
        )
        
        # Check basic connectivity first
        is_reachable, message = check_db_connection()
        logger.info("Connection check: %s", message)
        
        try:
            # Try to create database tables
            Base.metadata.create_all(bind=engine)
            logger.info("Successfully created database tables")
            
            # Verify connection with a simple query
            result = db.execute("SELECT version()").scalar()
            logger.info("Connected to PostgreSQL version: %s", result)
            return
            
        except OperationalError as e:
            logger.error(
                "Database connection failed (attempt %d/%d):\n%s",
                current_try,
                max_retries,
                str(e)
            )
            
        except ProgrammingError as e:
            logger.error(
                "Database schema error (attempt %d/%d):\n%s",
                current_try,
                max_retries,
                str(e)
            )
            
        except Exception as e:
            logger.error(
                "Unexpected error (attempt %d/%d):\n%s",
                current_try,
                max_retries,
                str(e)
            )

        if current_try < max_retries:
            logger.info("Waiting %d seconds before retrying...", retry_delay)
            time.sleep(retry_delay)
            retry_delay *= 2
        
        current_try += 1
    
    error_msg = (
        f"Failed to initialize database after {max_retries} attempts.\n"
        f"Last known configuration:\n"
        f"Host: {settings.DB_HOST}\n"
        f"Port: {settings.DB_PORT}\n"
        f"Database: {settings.DB_NAME}\n"
        f"User: {settings.DB_USER}"
    )
    logger.error(error_msg)
    raise Exception(error_msg)

def main() -> None:
    """Main initialization function"""
    logger.info(
        "Starting database initialization for %s environment",
        settings.API_ENV
    )
    init_db(db=SessionLocal())
    logger.info("Database initialization completed")

if __name__ == "__main__":
    main()
