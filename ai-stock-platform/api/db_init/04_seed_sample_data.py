#!/usr/bin/env python3
"""
Seed sample data for QuantumVestAI application development.
This script is streamlined for Kubernetes execution.
"""

import argparse
import json
import logging
import os
import random
import sys
from datetime import datetime, timedelta

import psycopg2
import psycopg2.extras
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db-init')

def get_db_connection():
    """Get database connection from environment variables."""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', os.environ.get('POSTGRES_SERVER')),
        database=os.environ.get('DB_NAME', os.environ.get('POSTGRES_DB')),
        user=os.environ.get('DB_USER', os.environ.get('POSTGRES_USER')),
        password=os.environ.get('DB_PASSWORD', os.environ.get('POSTGRES_PASSWORD')),
        port=os.environ.get('DB_PORT', os.environ.get('POSTGRES_PORT', '5432'))
    )

def seed_stocks():
    """Seed stock data into the database."""
    # Top stocks for sample data
    stocks = [
        {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology"},
        {"ticker": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology"},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "sector": "Technology"},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical"},
        {"ticker": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "sector": "Technology"},
        {"ticker": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical"},
        {"ticker": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology"},
        {"ticker": "BRK-B", "name": "Berkshire Hathaway Inc.", "exchange": "NYSE", "sector": "Financial Services"},
        {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "sector": "Financial Services"},
        {"ticker": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "sector": "Healthcare"}
    ]
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        logger.info(f"Adding {len(stocks)} sample stocks...")
        
        for stock in stocks:
            cur.execute("""
                INSERT INTO stocks (ticker, name, exchange, sector, last_updated)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (ticker) DO UPDATE SET
                    name = EXCLUDED.name,
                    exchange = EXCLUDED.exchange,
                    sector = EXCLUDED.sector,
                    last_updated = EXCLUDED.last_updated
                RETURNING id
            """, (stock["ticker"], stock["name"], stock["exchange"], 
                  stock["sector"], datetime.utcnow()))
            
            stock["id"] = cur.fetchone()[0]
        
        conn.commit()
        logger.info("Sample stocks added successfully")
        return stocks
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error seeding stocks: {e}")
        return []
    
    finally:
        cur.close()
        conn.close()

def seed_stock_prices(stocks):
    """Generate synthetic stock price data for the past year."""
    if not stocks:
        logger.error("No stocks provided for price seeding")
        return
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        logger.info("Generating synthetic stock price data...")
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        current_date = start_date
        
        # Base prices for each stock (roughly based on actual values)
        base_prices = {
            "AAPL": 150.0, "MSFT": 300.0, "GOOGL": 2000.0, "AMZN": 2500.0, 
            "META": 200.0, "TSLA": 800.0, "NVDA": 400.0, "BRK-B": 300.0,
            "JPM": 150.0, "JNJ": 170.0
        }
        
        # Start a transaction
        conn.autocommit = False
        
        # For each day in the date range
        while current_date <= end_date:
            for stock in stocks:
                ticker = stock["ticker"]
                base_price = base_prices.get(ticker, 100.0)
                
                # Generate synthetic prices with realistic volatility
                daily_volatility = random.uniform(-0.03, 0.03)
                close_price = base_price * (1 + daily_volatility)
                high_price = close_price * (1 + random.uniform(0, 0.02))
                low_price = close_price * (1 - random.uniform(0, 0.02))
                open_price = close_price * (1 + random.uniform(-0.015, 0.015))
                
                # Generate realistic volume
                volume = int(random.uniform(1000000, 50000000))
                
                # Update the base price for the next day
                base_prices[ticker] = close_price
                
                # Insert price data
                cur.execute("""
                    INSERT INTO stock_prices 
                    (stock_id, date, open, high, low, close, adjusted_close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_id, date) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        adjusted_close = EXCLUDED.adjusted_close,
                        volume = EXCLUDED.volume
                """, (
                    stock["id"], 
                    current_date,
                    round(open_price, 2),
                    round(high_price, 2),
                    round(low_price, 2),
                    round(close_price, 2),
                    round(close_price, 2),  # Adjusted close same as close for simplicity
                    volume
                ))
            
            # Move to the next day
            current_date += timedelta(days=1)
            
            # Commit every 30 days to avoid huge transactions
            if current_date.day == 1 or current_date >= end_date:
                conn.commit()
                logger.info(f"Committed data up to {current_date}")
        
        logger.info("Stock price data generated successfully")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error seeding stock prices: {e}")
    
    finally:
        cur.close()
        conn.close()

def seed_watchlists():
    """Create sample watchlists for users."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if we have users and stocks
        cur.execute("SELECT id FROM users LIMIT 5")
        users = cur.fetchall()
        
        cur.execute("SELECT id FROM stocks LIMIT 10")
        stocks = cur.fetchall()
        
        if not users or not stocks:
            logger.warning("Not enough users or stocks to create watchlists")
            return
        
        logger.info("Creating sample watchlists...")
        
        for user_id in [row[0] for row in users]:
            # Select 3-5 random stocks for each user
            num_stocks = random.randint(3, 5)
            selected_stocks = random.sample([row[0] for row in stocks], num_stocks)
            
            for stock_id in selected_stocks:
                # Add to watchlist with a random note
                notes = random.choice([
                    "Watching for earnings",
                    "Potential breakout",
                    "Long-term investment",
                    "Technical analysis looks good",
                    "Fundamentals are strong",
                    None
                ])
                
                cur.execute("""
                    INSERT INTO user_watchlist (user_id, stock_id, notes, added_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id, stock_id) DO NOTHING
                """, (user_id, stock_id, notes, datetime.utcnow()))
        
        conn.commit()
        logger.info("Sample watchlists created successfully")
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating sample watchlists: {e}")
    
    finally:
        cur.close()
        conn.close()

def main():
    """Main function for seeding sample data."""
    parser = argparse.ArgumentParser(description="Seed sample data for QuantumVestAI")
    parser.add_argument("--env", choices=["development", "production"], 
                        default=os.environ.get("ENVIRONMENT", "development"))
    
    args = parser.parse_args()
    
    # Only proceed in development environment or if forced
    if args.env == "production" and os.environ.get("FORCE_SEED") != "true":
        logger.warning("Skipping sample data seeding in production environment")
        return
    
    # Seed the database
    try:
        # Seed stocks
        stocks = seed_stocks()
        
        # Seed stock prices
        seed_stock_prices(stocks)
        
        # Create sample watchlists
        seed_watchlists()
        
        logger.info("Sample data seeding completed successfully")
    
    except Exception as e:
        logger.error(f"Error seeding sample data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
