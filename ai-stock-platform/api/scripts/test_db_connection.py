"""
Database Connection Test Script
Created: 2025-05-19 05:56:45
Author: daparthi001
"""
import pytest
pytest.skip("Manual script", allow_module_level=True)
import logging
from sqlalchemy import text
from db.session import SessionLocal
from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection and configuration"""
    try:
        db = SessionLocal()
        # Test connection
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
        logger.info("Database connection successful!")
        
        # Test connection settings
        result = db.execute(text("""
            SELECT name, setting 
            FROM pg_settings 
            WHERE name LIKE 'tcp_keepalives%'
        """))
        settings_data = dict(result.fetchall())
        logger.info("PostgreSQL TCP Keepalive settings:")
        for name, value in settings_data.items():
            logger.info(f"{name}: {value}")
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info(f"Testing connection to: {settings.POSTGRES_SERVER}")
    test_database_connection()
