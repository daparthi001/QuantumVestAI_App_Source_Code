"""
Database session management
Created: 2025-05-19 03:25:32
Author: daparthi001
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()