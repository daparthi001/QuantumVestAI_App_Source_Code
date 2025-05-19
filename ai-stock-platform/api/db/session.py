"""
Database Session Management
Created: 2025-05-19 04:05:44
Author: daparthi001
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.core.config import settings

engine = create_engine(
    str(settings.DATABASE_URI),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)