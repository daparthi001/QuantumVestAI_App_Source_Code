"""
Database Session Module
Created: 2025-05-21 18:19:56
Author: daparthi001
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from core.config import settings

# Create database engine with optimal RDS connection settings
engine: Engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Maximum number of connections to allow above pool_size
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "application_name": "stock_portfolio_api"  # Identify application in RDS logs
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()