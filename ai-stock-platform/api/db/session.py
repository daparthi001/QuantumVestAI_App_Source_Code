"""
Database Session Module
Created: 2025-05-22 05:06:41
Author: daparthi001
Updated: 2025-06-14 23:14:45 by daparthi001
"""
import logging
import time
import os
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from db.base import Base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Defensive import strategy
try:
    # Try the correct import path first
    from core.config.settings import settings
    logger.info("Successfully imported settings from core.config.settings")
except ImportError:
    try:
        # Try alternate import path
        from core.config import settings
        logger.info("Successfully imported settings from core.config")
    except ImportError:
        # Create fallback settings if all imports fail
        logger.error("Failed to import settings, using environment variables directly")
        
        class FallbackSettings:
            def __init__(self):
                self.DB_HOST = os.environ.get("DB_HOST", "localhost")
                self.DB_PORT = os.environ.get("DB_PORT", "5432")
                self.DB_NAME = os.environ.get("DB_NAME", "quantumvestaidb")
                self.DB_USER = os.environ.get("DB_USER", "dbadmin")
                self._DB_PASSWORD = os.environ.get("DB_PASSWORD", "75LerK%0_J<t$H}Z")
                self.API_ENV = os.environ.get("API_ENV", "development")
            
            def get_db_url(self):
                return f"postgresql://{self.DB_USER}:{self._DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        
        settings = FallbackSettings()

def create_db_engine(retries: int = 3, delay: int = 5):
    """Create database engine with retry logic"""
    for attempt in range(retries):
        try:
            # Get database connection parameters
            db_host = getattr(settings, 'DB_HOST', os.environ.get('DB_HOST', 'localhost'))
            db_port = getattr(settings, 'DB_PORT', os.environ.get('DB_PORT', '5432'))
            db_name = getattr(settings, 'DB_NAME', os.environ.get('DB_NAME', 'quantumvestaidb'))
            db_user = getattr(settings, 'DB_USER', os.environ.get('DB_USER', 'dbadmin'))
            api_env = getattr(settings, 'API_ENV', os.environ.get('API_ENV', 'development'))
            
            logger.info(
                "Attempting database connection (attempt %d/%d) to %s:%s",
                attempt + 1,
                retries,
                db_host,
                db_port
            )
            
            # Get database URL with proper password handling
            if hasattr(settings, 'get_db_url') and callable(settings.get_db_url):
                db_url = settings.get_db_url()
            else:
                # Fallback for password
                db_password = os.environ.get('DB_PASSWORD', '75LerK%0_J<t$H}Z')
                if hasattr(settings, 'DB_PASSWORD'):
                    if hasattr(settings.DB_PASSWORD, 'get_secret_value') and callable(settings.DB_PASSWORD.get_secret_value):
                        db_password = settings.DB_PASSWORD.get_secret_value()
                    else:
                        db_password = settings.DB_PASSWORD
                
                db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
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
                    "application_name": f"quantumvestai_{api_env}",
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
    # Create a mock engine and session for minimal functionality
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///fallback.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.warning("Using fallback SQLite database due to connection error")
    # Automatically create tables for the fallback database so basic
    # authentication and other features continue working when PostgreSQL
    # is unavailable.
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Initialized fallback SQLite database")
    except Exception as init_err:
        logger.error("Failed to initialize fallback database: %s", str(init_err))

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()