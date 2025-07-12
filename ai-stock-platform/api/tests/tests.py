"""
Database Connection Test Script
Created: 2025-05-22 00:05:34
Author: daparthi001
"""
import os
import logging
import psycopg2
from time import sleep

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_config():
    """Get database configuration from environment variables"""
    config = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

    # Check for missing configuration
    missing_vars = [k for k, v in config.items() if not v]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    logger.info(
        "Database configuration:\n"
        "Host: %s\n"
        "Port: %s\n"
        "Database: %s\n"
        "User: %s",
        config['host'],
        config['port'],
        config['database'],
        config['user']
    )

    return config

def test_connection(max_retries=3, retry_delay=5):
    """Test database connection with retry logic"""
    config = get_db_config()
    
    for attempt in range(max_retries):
        try:
            logger.info(
                "Attempting database connection (%d/%d) to %s:%s",
                attempt + 1,
                max_retries,
                config['host'],
                config['port']
            )

            # Attempt connection
            conn = psycopg2.connect(**config)
            
            # Test the connection
            with conn.cursor() as cur:
                cur.execute('SELECT version()')
                version = cur.fetchone()
                logger.info("Successfully connected to PostgreSQL %s", version[0])
            
            conn.close()
            return True

        except Exception as e:
            logger.error(
                "Connection attempt %d/%d failed: %s",
                attempt + 1,
                max_retries,
                str(e)
            )
            
            if attempt < max_retries - 1:
                logger.info("Retrying in %d seconds...", retry_delay)
                sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All connection attempts failed")
                return False

if __name__ == "__main__":
    try:
        if test_connection():
            logger.info("Database connection test succeeded")
            exit(0)
        else:
            logger.error("Database connection test failed")
            exit(1)
    except Exception as e:
        logger.error("Error: %s", str(e))
        exit(1)
