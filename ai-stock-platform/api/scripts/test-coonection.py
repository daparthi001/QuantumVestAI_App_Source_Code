"""
Configuration Test Script
Created: 2025-05-22 05:06:41
Author: daparthi001
"""
import os
import logging
from core.config import Settings
from core.config.settings import settings, get_db_url

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_settings():
    """Test settings configuration"""
    try:
        # Set environment variables
        os.environ.update({
            'DB_HOST': 'quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com',
            'DB_PORT': '5432',
            'DB_NAME': 'quantumvestaidb',
            'DB_USER': 'dbadmin',
            'DB_PASSWORD': '75LerK%0_J<t$H}Z'
        })
        
        # Create settings instance
        settings = Settings()
        
        # Test database URL construction
        db_url = settings.get_db_url()
        
        logger.info("Settings loaded successfully")
        logger.info("Database URL constructed (password hidden)")
        
        return True
        
    except Exception as e:
        logger.error("Settings test failed: %s", str(e))
        return False

if __name__ == "__main__":
    test_settings()