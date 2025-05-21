"""
Database Connection Test Tool
Created: 2025-05-21 19:19:45
Author: daparthi001
"""
import sys
import logging
from sqlalchemy import text
import socket
from contextlib import closing

from db.session import SessionLocal
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_network_connection() -> bool:
    """Test TCP connection to database"""
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(5)
            result = sock.connect_ex((settings.DB_HOST, int(settings.DB_PORT)))
            if result == 0:
                logger.info("Network connection to database successful")
                return True
            else:
                logger.error("Network connection to database failed")
                return False
    except Exception as e:
        logger.error("Network connection test failed: %s", str(e))
        return False

def test_database_connection() -> bool:
    """Test database connection and permissions"""
    try:
        db = SessionLocal()
        # Test basic connection
        version = db.execute(text("SELECT version()")).scalar()
        logger.info("Connected to PostgreSQL version: %s", version)
        
        # Test permissions
        db.execute(text("SELECT 1"))
        logger.info("Database permissions verified")
        
        db.close()
        return True
    except Exception as e:
        logger.error("Database connection test failed: %s", str(e))
        return False

def main():
    """Main test function"""
    logger.info("Starting database connection tests...")
    
    # Test network connection
    if not test_network_connection():
        logger.error("Network connection test failed!")
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        logger.error("Database connection test failed!")
        sys.exit(1)
    
    logger.info("All database connection tests passed successfully!")

if __name__ == "__main__":
    main()