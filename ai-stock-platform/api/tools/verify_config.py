"""
Configuration Verification Tool
Created: 2025-05-21 19:07:45
Author: daparthi001
"""
import logging
import os
import sys

from core.config import settings
from db.session import SessionLocal
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_environment():
    """Verify environment variables"""
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    
    logger.info("Checking environment variables...")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.info("%s is set to: %s", var, '*' * len(value) if 'PASSWORD' in var else value)
        else:
            logger.error("%s is not set!", var)
            return False
    return True

def verify_database_connection():
    """Verify database connection"""
    logger.info("Verifying database connection...")
    
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT version()")).scalar()
        logger.info("Successfully connected to PostgreSQL version: %s", result)
        db.close()
        return True
    except Exception as e:
        logger.error("Failed to connect to database: %s", str(e))
        return False

def main():
    """Main verification function"""
    logger.info("Starting configuration verification...")
    
    if not verify_environment():
        logger.error("Environment verification failed!")
        sys.exit(1)
    
    if not verify_database_connection():
        logger.error("Database connection verification failed!")
        sys.exit(1)
    
    logger.info("All verification checks passed successfully!")

if __name__ == "__main__":
    main()
