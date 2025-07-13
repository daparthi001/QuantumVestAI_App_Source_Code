"""
Database Connection Test Script
Created: 2025-05-22 04:54:08
Author: daparthi001
"""
import pytest

pytest.skip("Requires SQLAlchemy", allow_module_level=True)
import logging
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
config = {
    'host': 'quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com',
    'port': '5432',
    'database': 'quantumvestaidb',
    'user': 'dbadmin',
    'password': '75LerK%0_J<t$H}Z'
}

def test_connection():
    """Test database connection"""
    try:
        # Create connection URL with escaped password
        password = quote_plus(config['password'])
        db_url = (
            f"postgresql://{config['user']}:{password}"
            f"@{config['host']}:{config['port']}/{config['database']}"
        )

        # Create engine
        engine = create_engine(
            db_url,
            connect_args={
                "connect_timeout": 10,
                "application_name": "quantumvestai_test",
                "sslmode": "require"
            }
        )

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).scalar()
            logger.info("Successfully connected to PostgreSQL: %s", result)
            
            # Test database permissions
            conn.execute(text("SELECT current_user")).scalar()
            logger.info("Database permissions verified")
            
            return True
            
    except Exception as e:
        logger.error("Connection test failed: %s", str(e))
        return False

if __name__ == "__main__":
    test_connection()
