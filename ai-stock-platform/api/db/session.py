"""
Database session management module
Created: 2025-05-19 02:50:53 UTC
Author: daparthi001
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with pool configuration
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    Created: 2025-05-19 02:50:53 UTC
    Author: daparthi001
    
    Yields:
        Session: SQLAlchemy session
    
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()
