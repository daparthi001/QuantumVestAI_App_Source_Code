#!/usr/bin/env python3
"""
Seed data initialization for QuantumVestAI database
Created: 2025-05-15 20:23:18
Author: daparthi001
"""
import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.models import User, Stock, Watchlist, WatchlistStock

def seed_data():
    """Seed initial data into the database"""
    logger.info("Starting database seeding process")
    
    # Get database connection details from environment
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'postgres')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'quantumvestai')
    
    # Create database connection
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if data already exists
        user_count = session.query(User).count()
        if user_count > 0:
            logger.info(f"Database already contains {user_count} users. Skipping seed data.")
            return
            
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@quantumvest.ai",
            password_hash=pwd_context.hash("admin123"),
            first_name="System",
            last_name="Admin",
            is_active=True,
            is_admin=True
        )
        session.add(admin_user)
        
        # Create demo user
        demo_user = User(
            username="demo",
            email="demo@quantumvest.ai",
            password_hash=pwd_context.hash("demo123"),
            first_name="Demo",
            last_name="User",
            is_active=True,
            is_admin=False
        )
        session.add(demo_user)
        session.flush()
        
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
        session.add_all(stocks)
        session.flush()
        
        # Create watchlist for demo user
        watchlist = Watchlist(
            user_id=demo_user.id,
            name="Tech Giants",
            description="Major technology companies",
            is_public=True
        )
        session.add(watchlist)
        session.flush()
        
        # Add stocks to watchlist
        tech_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        for ticker in tech_tickers:
            watchlist_stock = WatchlistStock(
                watchlist_id=watchlist.id,
                stock_ticker=ticker
            )
            session.add(watchlist_stock)
        
        # Commit the transaction
        session.commit()
        logger.info("Database seeding completed successfully")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error during database seeding: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_data()
