"""
Database initialization module for QuantumVestAI.

This module handles database verification and initialization
during application startup.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from core.config import settings
from db.models.user import User
from db.session import engine, get_db
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def verify_database_connection():
    """Verify that the database connection is working."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Database connection verified successfully")
                return True
            else:
                logger.error("Database connection verification failed")
                return False
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        return False

def verify_database_schema():
    """Verify that the database schema exists."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ["users", "stocks", "stock_prices", "forecast_models", 
                          "forecasts", "whitepapers", "whitepaper_analyses"]
        
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"Missing database tables: {missing_tables}")
            return False
        
        logger.info("Database schema verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error verifying database schema: {e}")
        return False

def verify_admin_exists():
    """Verify that at least one admin user exists."""
    try:
        db = next(get_db())
        admin = db.query(User).filter(User.role == "admin").first()
        db.close()
        
        if admin:
            logger.info(f"Admin user verified: {admin.username}")
            return True
        
        logger.warning("No admin user found in database")
        return False
    except Exception as e:
        logger.error(f"Error verifying admin user: {e}")
        return False

def verify_essential_data():
    """Verify that essential reference data exists."""
    try:
        db = next(get_db())
        
        # Check if forecast models exist
        forecast_models = db.execute(text("SELECT COUNT(*) FROM forecast_models")).scalar()
        if forecast_models == 0:
            logger.warning("No forecast models found in database")
            return False
        
        # Check if market sectors exist
        try:
            market_sectors = db.execute(text("SELECT COUNT(*) FROM market_sectors")).scalar()
            if market_sectors == 0:
                logger.warning("No market sectors found in database")
                return False
        except:
            logger.warning("Market sectors table does not exist")
        
        db.close()
        logger.info("Essential reference data verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error verifying essential data: {e}")
        return False

def run_database_verification():
    """Run all database verification checks."""
    connection_ok = verify_database_connection()
    if not connection_ok:
        logger.error("Database connection verification failed")
        return False
    
    schema_ok = verify_database_schema()
    admin_ok = verify_admin_exists()
    data_ok = verify_essential_data()
    
    all_ok = schema_ok and admin_ok and data_ok
    
    if all_ok:
        logger.info("All database verifications passed successfully")
    else:
        logger.warning("Some database verifications failed")
        
    return all_ok

def initialize_database():
    """Initialize database if needed during application startup."""
    # Only run verification in production, not initialization
    if settings.ENVIRONMENT.lower() == "production":
        logger.info("Production environment detected, running database verification only")
        return run_database_verification()
    
    # In non-production environments, we can attempt to initialize if verification fails
    verified = run_database_verification()
    if verified:
        return True
    
    logger.info("Database verification failed, attempting initialization")
    
    try:
        # Run alembic migrations if schema verification failed
        if not verify_database_schema():
            logger.info("Running database migrations")
            from alembic import command
            from alembic.config import Config
            
            # Alembic configuration is located in the api package root
            api_root = Path(__file__).resolve().parents[2]
            alembic_cfg = Config(str(api_root / "alembic.ini"))

            command.upgrade(alembic_cfg, "head")
        
        # Create admin user if none exists
        if not verify_admin_exists() and settings.ADMIN_PASSWORD:
            logger.info("Creating default admin user")
            from models.user import create_admin_user
            create_admin_user(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                full_name=settings.ADMIN_FULL_NAME
            )
        
        # Initialize reference data if needed
        if not verify_essential_data():
            logger.info("Initializing essential reference data")
            # Execute reference data script
            with engine.begin() as conn:
                ref_sql = api_root / "db_init" / "02_reference_data.sql"

                with open(ref_sql) as f:
                    conn.execute(text(f.read()))
        
        logger.info("Database initialization completed")
        return True
    
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

# Add this to api/main.py startup event
# @app.on_event("startup")
# async def startup_db():
#     initialize_database()
