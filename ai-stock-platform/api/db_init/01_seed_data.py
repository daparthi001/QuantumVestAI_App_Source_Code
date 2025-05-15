#!/usr/bin/env python3
"""
Seed data initialization for QuantumVestAI database
Created: 2025-05-15 17:11:05
Author: daparthi001
"""
import os
import sys
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

# Set up paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import models
from models.user import User
from models.stock import Stock
from models.watchlist import Watchlist
from models.watchlist_stock import WatchlistStock
from db.session import get_db

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    """Seed initial data into the database"""
    logger.info("Starting database seeding process")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@quantumvest.ai",
            password_hash=pwd_context.hash("admin123"),
            first_name="System",
            last_name="Admin",
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.flush()  # Flush to get the ID
        logger.info("Admin user created")
        
        # Create demo user
        demo_user = User(
            username="demo",
            email="demo@quantumvest.ai",
            password_hash=pwd_context.hash("demo123"),
            first_name="Demo",
            last_name="User",
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(demo_user)
        db.flush()  # Flush to get the ID
        logger.info("Demo user created")
        
        # Create stocks
        stocks = [
            Stock(ticker="AAPL", company_name="Apple Inc.", sector="Technology", 
                  industry="Consumer Electronics", country="USA"),
            Stock(ticker="MSFT", company_name="Microsoft Corporation", sector="Technology", 
                  industry="Software—Infrastructure", country="USA"),
            Stock(ticker="AMZN", company_name="Amazon.com Inc.", sector="Consumer Cyclical", 
                  industry="Internet Retail", country="USA"),
            Stock(ticker="GOOGL", company_name="Alphabet Inc.", sector="Communication Services", 
                  industry="Internet Content & Information", country="USA"),
            Stock(ticker="TSLA", company_name="Tesla Inc.", sector="Consumer Cyclical", 
                  industry="Auto Manufacturers", country="USA"),
            Stock(ticker="META", company_name="Meta Platforms Inc.", sector="Communication Services", 
                  industry="Internet Content & Information", country="USA"),
            Stock(ticker="NVDA", company_name="NVIDIA Corporation", sector="Technology", 
                  industry="Semiconductors", country="USA"),
            Stock(ticker="JPM", company_name="JPMorgan Chase & Co.", sector="Financial Services", 
                  industry="Banks—Diversified", country="USA"),
            Stock(ticker="V", company_name="Visa Inc.", sector="Financial Services", 
                  industry="Credit Services", country="USA"),
            Stock(ticker="JNJ", company_name="Johnson & Johnson", sector="Healthcare", 
                  industry="Drug Manufacturers—General", country="USA")
        ]
        db.add_all(stocks)
        db.flush()
        logger.info(f"{len(stocks)} stocks created")
        
        # Create watchlist for demo user
        watchlist = Watchlist(
            user_id=demo_user.id,
            name="Tech Giants",
            description="Major technology companies",
            is_public=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(watchlist)
        db.flush()
        logger.info("Demo user watchlist created")
        
        # Add stocks to watchlist
        tech_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        watchlist_stocks = []
        for ticker in tech_tickers:
            watchlist_stocks.append(
                WatchlistStock(
                    watchlist_id=watchlist.id,
                    stock_ticker=ticker,
                    added_at=datetime.utcnow()
                )
            )
        db.add_all(watchlist_stocks)
        logger.info(f"Added {len(tech_tickers)} stocks to demo user watchlist")
        
        # Commit the transaction
        db.commit()
        logger.info("Database seeding completed successfully")
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during seeding: {str(e)}")
        logger.info("Continuing with the process - data might already exist")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during database seeding: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()