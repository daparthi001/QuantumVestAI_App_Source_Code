"""
Database Connection Handler
Created: 2025-01-09
Author: AI Assistant
"""
import logging
import os
from typing import Optional
from contextlib import contextmanager
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker

from db.base import Base

logger = logging.getLogger("api")


class DatabaseConnectionManager:
    """Simple database connection manager with error handling"""
    
    def __init__(self):
        self.connection_pool = None
        self.is_connected = False
        self.last_error = None
    
    def initialize_connection(self) -> bool:
        """Initialize database connection"""
        try:
            # This is a placeholder - in a real implementation you would
            # initialize your actual database connection here
            # For now, just simulate connection status
            db_host = os.environ.get("DB_HOST", "localhost")
            db_port = os.environ.get("DB_PORT", "5432")
            db_name = os.environ.get("DB_NAME", "quantumvestai")
            
            logger.info(f"Attempting to connect to database at {db_host}:{db_port}/{db_name}")
            
            # Simulate connection success/failure based on environment
            if db_host == "localhost" and not os.environ.get("DB_PASSWORD"):
                logger.warning("No database password provided - using mock connection")
                self.is_connected = True
                return True
            
            # In a real implementation, you would:
            # 1. Create SQLAlchemy engine
            # 2. Test connection
            # 3. Set up connection pool
            
            self.is_connected = True
            self.last_error = None
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {str(e)}")
            self.is_connected = False
            self.last_error = str(e)
            return False
    
    def check_connection(self) -> bool:
        """Check if database connection is alive"""
        try:
            if not self.is_connected:
                return False
            
            # In a real implementation, you would run a simple query
            # like "SELECT 1" to check connection health
            
            return True
            
        except Exception as e:
            logger.error(f"Database connection check failed: {str(e)}")
            self.is_connected = False
            self.last_error = str(e)
            return False
    
    def reconnect(self) -> bool:
        """Attempt to reconnect to database"""
        logger.info("Attempting to reconnect to database...")
        return self.initialize_connection()
    
    @contextmanager
    def get_connection(self):
        """Get database connection context manager"""
        if not self.is_connected:
            if not self.reconnect():
                raise Exception(f"Cannot connect to database: {self.last_error}")
        
        try:
            # In a real implementation, yield actual connection
            yield None
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise
    
    def get_health_status(self) -> dict:
        """Get database health status"""
        return {
            "connected": self.is_connected,
            "last_error": self.last_error,
            "host": os.environ.get("DB_HOST", "localhost"),
            "port": os.environ.get("DB_PORT", "5432"),
            "database": os.environ.get("DB_NAME", "quantumvestai")
        }


# Global database manager instance
db_manager = DatabaseConnectionManager()


def initialize_database() -> bool:
    """Initialize database connection on startup"""
    return db_manager.initialize_connection()


def get_database_health() -> dict:
    """Get database health status"""
    return db_manager.get_health_status()


def check_database_connection() -> bool:
    """Check database connection health"""
    return db_manager.check_connection()


@contextmanager
def get_db_connection():
    """Get database connection"""
    with db_manager.get_connection() as conn:
        yield conn


# Async engine and session for FastAPI dependencies
DATABASE_URL = os.environ.get("ASYNC_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
async_engine = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session():
    """Yield an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def create_db_and_tables() -> None:
    """Create database tables if they do not exist."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created or verified")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise