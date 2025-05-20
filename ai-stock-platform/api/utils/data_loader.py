"""
Utility functions for loading stock market data.

These functions handle fetching data from various sources,
including APIs, databases, and local files.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
import os
from sqlalchemy.orm import Session

from core.config import settings
from db.models.stock import Stock, StockPrice
from core.exceptions import ExternalAPIError

logger = logging.getLogger("api")

async def load_stock_data(
    ticker: str,
    period: str = "1y",
    session: Optional[aiohttp.ClientSession] = None,
    use_cache: bool = True
) -> pd.DataFrame:
    """
    Load historical stock data for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max")
        session: Aiohttp client session
        use_cache: Whether to use cached data if available
        
    Returns:
        DataFrame with historical price data
    """
    try:
        # In a production environment, this would fetch from an external API
        # For this implementation, we'll generate mock data
        
        # Check cache first if enabled
        if use_cache:
            cached_data = _get_cached_data(ticker, period)
            if cached_data is not None:
                return cached_data
        
        # Generate mock data
        df = _generate_mock_stock_data(ticker, period)
        
        # Cache the data
        if use_cache:
            _cache_data(ticker, period, df)
        
        return df
    
    except Exception as e:
        logger.exception(f"Error loading stock data for {ticker}: {e}")
        # Return empty dataframe with correct columns
        return pd.DataFrame(columns=[
            "date", "ticker", "open", "high", "low", "close", "volume", "adjusted_close"
        ])

async def load_market_data(
    index_symbol: str = "^GSPC",  # S&P 500 by default
    period: str = "1y",
    session: Optional[aiohttp.ClientSession] = None
) -> pd.DataFrame:
    """
    Load market index data.
    
    Args:
        index_symbol: Market index symbol
        period: Time period
        session: Aiohttp client session
        
    Returns:
        DataFrame with market index data
    """
    try:
        # Similar to load_stock_data, but for market indices
        return await load_stock_data(index_symbol, period, session)
    
    except Exception as e:
        logger.exception(f"Error loading market data for {index_symbol}: {e}")
        return pd.DataFrame(columns=[
            "date", "ticker", "open", "high", "low", "close", "volume", "adjusted_close"
        ])

async def get_ticker_info(
    ticker: str,
    session: Optional[aiohttp.ClientSession] = None
) -> Dict[str, Any]:
    """
    Get basic information for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        session: Aiohttp client session
        
    Returns:
        Dictionary with stock information
    """
    try:
        # In a production environment, this would fetch from an external API
        # For this implementation, we'll generate mock data
        
        # Generate a deterministic "random" seed based on ticker
        seed = sum(ord(c) for c in ticker)
        np.random.seed(seed)
        
        # Basic stock information
        sectors = [
            "Technology", "Healthcare", "Financial Services", "Consumer Cyclical",
            "Communication Services", "Industrials", "Consumer Defensive", "Energy",
            "Basic Materials", "Real Estate", "Utilities"
        ]
        
        industries = {
            "Technology": ["Software", "Hardware", "Semiconductors", "IT Services", "Electronic Components"],
            "Healthcare": ["Biotechnology", "Pharmaceuticals", "Medical Devices", "Healthcare Services", "Health Insurance"],
            "Financial Services": ["Banks", "Insurance", "Asset Management", "Fintech", "REITs"],
            "Consumer Cyclical": ["Retail", "Automotive", "Entertainment", "Restaurants", "Apparel"],
            "Communication Services": ["Telecom", "Media", "Social Media", "Advertising", "Entertainment"],
            "Industrials": ["Aerospace", "Defense", "Construction", "Machinery", "Transportation"],
            "Consumer Defensive": ["Food", "Beverages", "Household Products", "Personal Products", "Tobacco"],
            "Energy": ["Oil & Gas", "Renewable Energy", "Energy Services", "Pipelines", "Coal"],
            "Basic Materials": ["Chemicals", "Metals & Mining", "Paper & Forest Products", "Construction Materials", "Containers & Packaging"],
            "Real Estate": ["Residential", "Commercial", "Industrial", "Retail", "Specialized"],
            "Utilities": ["Electric", "Water", "Gas", "Multi-Utilities", "Independent Power Producers"]
        }
        
        exchanges = ["NYSE", "NASDAQ", "AMEX"]
        countries = ["USA", "Canada", "UK", "Germany", "Japan", "China", "Australia", "Brazil", "India"]
        
        # Select sector based on first letter of ticker
        sector_idx = ord(ticker[0].upper()) % len(sectors)
        sector = sectors[sector_idx]
        
        # Select industry from the sector
        industry_list = industries.get(sector, ["General"])
        industry_idx = ord(ticker[-1].upper()) % len(industry_list)
        industry = industry_list[industry_idx]
        
        # Generate some plausible financial metrics
        market_cap = np.random.randint(1, 1000) * 1e6  # $1M to $1000B
        pe_ratio = np.random.uniform(5, 50)
        dividend_yield = np.random.uniform(0, 5)
        beta = np.random.uniform(0.5, 2.0)
        eps = np.random.uniform(0.5, 10)
        
        # Generate current price
        price = np.random.uniform(10, 500)
        
        # Create ticker info object
        info = {
            "ticker": ticker,
            "name": f"{ticker.upper()} Corporation",  # Mock name
            "exchange": np.random.choice(exchanges),
            "sector": sector,
            "industry": industry,
            "country": np.random.choice(countries),
            "market_cap": market_cap,
            "pe_ratio": round(pe_ratio, 2),
            "dividend_yield": round(dividend_yield, 2),
            "beta": round(beta, 2),
            "eps": round(eps, 2),
            "last_price": round(price, 2),
            "currency": "USD",
            "last_updated": datetime.utcnow().isoformat(),
            "website": f"https://www.{ticker.lower()}.com",
            "employees": np.random.randint(100, 100000)
        }
        
        return info
    
    except Exception as e:
        logger.exception(f"Error getting ticker info for {ticker}: {e}")
        return {
            "ticker": ticker,
            "name": f"{ticker.upper()}",
            "error": str(e)
        }

async def get_historical_prices(
    ticker: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Optional[Session] = None
) -> pd.DataFrame:
    """
    Get historical prices for a ticker from database or external source.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in format YYYY-MM-DD
        end_date: End date in format YYYY-MM-DD
        db: Database session
        
    Returns:
        DataFrame with historical price data
    """
    try:
        # If database session provided, try to get from database first
        if db:
            stock = db.query(Stock).filter(Stock.ticker == ticker).first()
            if stock:
                query = db.query(StockPrice).filter(StockPrice.stock_id == stock.id)
                
                if start_date:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    query = query.filter(StockPrice.date >= start_dt)
                
                if end_date:
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    query = query.filter(StockPrice.date <= end_dt)
                
                prices = query.order_by(StockPrice.date).all()
                
                if prices:
                    # Convert to DataFrame
                    df = pd.DataFrame([
                        {
                            "date": price.date,
                            "ticker": ticker,
                            "open": price.open,
                            "high": price.high,
                            "low": price.low,
                            "close": price.close,
                            "adjusted_close": price.adjusted_close,
                            "volume": price.volume
                        }
                        for price in prices
                    ])
                    return df
        
        # If not in database or database not provided, load from external source
        # Parse dates if provided
        if start_date and end_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end_dt - start_dt).days
            
            # Map days to appropriate period
            if days <= 5:
                period = "5d"
            elif days <= 30:
                period = "1mo"
            elif days <= 90:
                period = "3mo"
            elif days <= 180:
                period = "6mo"
            elif days <= 365:
                period = "1y"
            elif days <= 730:
                period = "2y"
            elif days <= 1825:
                period = "5y"
            else:
                period = "max"
        else:
            # Default to 1 year if no dates specified
            period = "1y"
        
        # Load data
        df = await load_stock_data(ticker, period)
        
        # Filter by dates if provided
        if start_date:
            start_dt = pd.to_datetime(start_date)
            df = df[df["date"] >= start_dt]
        
        if end_date:
            end_dt = pd.to_datetime(end_date)
            df = df[df["date"] <= end_dt]
        
        return df
    
    except Exception as e:
        logger.exception(f"Error getting historical prices for {ticker}: {e}")
        return pd.DataFrame(columns=[
            "date", "ticker", "open", "high", "low", "close", "volume", "adjusted_close"
        ])

async def fetch_financials(
    ticker: str,
    session: Optional[aiohttp.ClientSession] = None
) -> Dict[str, Any]:
    """
    Fetch financial statements for a company.
    
    Args:
        ticker: Stock ticker symbol
        session: Aiohttp client session
        
    Returns:
        Dictionary with financial data
    """
    try:
        # In a production environment, this would fetch from an external API
        # For this implementation, we'll generate mock data
        
        # Generate a deterministic "random" seed based on ticker
        seed = sum(ord(c) for c in ticker)
        np.random.seed(seed)
        
        # Generate quarterly dates for the past 4 quarters
        now = datetime.now()
        quarters = []
        for i in range(4):
            quarter_date = (now - timedelta(days=90*i)).strftime("%Y-%m-%d")
            quarters.append(quarter_date)
        
        # Income Statement
        revenue_base = np.random.uniform(500e6, 10e9)
        revenue_growth = np.random.uniform(0.01, 0.1)
        
        income_statement = {
            "quarters": quarters,
            "revenue": [
                revenue_base * (1 + revenue_growth)**i for i in range(4)
            ],
            "cost_of_revenue": [
                revenue_base * (1 + revenue_growth)**i * np.random.uniform(0.5, 0.7) 
                for i in range(4)
            ],
            "gross_profit": [
                revenue_base * (1 + revenue_growth)**i * np.random.uniform(0.3, 0.5) 
                for i in range(4)
            ],
            "operating_expenses": [
                revenue_base * (1 + revenue_growth)**i * np.random.uniform(0.1, 0.3) 
                for i in range(4)
            ],
            "operating_income": [
                revenue_base * (1 + revenue_growth)**i * np.random.uniform(0.1, 0.3) 
                for i in range(4)
            ],
            "net_income": [
                revenue_base * (1 + revenue_growth)**i * np.random.uniform(0.05, 0.2) 
                for i in range(4)
            ],
            "eps": [
                np.random.uniform(0.5, 5.0) for _ in range(4)
            ]
        }
        
        # Balance Sheet
        assets_base = revenue_base * 2
        
        balance_sheet = {
            "quarters": quarters,
            "total_assets": [
                assets_base * (1 + np.random.uniform(0.01, 0.05))**i 
                for i in range(4)
            ],
            "total_liabilities": [
                assets_base * (1 + np.random.uniform(0.01, 0.05))**i * np.random.uniform(0.4, 0.6) 
                for i in range(4)
            ],
            "total_equity": [
                assets_base * (1 + np.random.uniform(0.01, 0.05))**i * np.random.uniform(0.4, 0.6) 
                for i in range(4)
            ],
            "cash_equivalents": [
                assets_base * np.random.uniform(0.05, 0.15) 
                for _ in range(4)
            ],
            "short_term_investments": [
                assets_base * np.random.uniform(0.05, 0.15) 
                for _ in range(4)
            ],
            "long_term_debt": [
                assets_base * np.random.uniform(0.2, 0.4) 
                for _ in range(4)
            ]
        }
        
        # Cash Flow Statement
        cash_flow = {
            "quarters": quarters,
            "operating_cash_flow": [
                revenue_base * np.random.uniform(0.1, 0.3) 
                for _ in range(4)
            ],
            "capital_expenditures": [
                -revenue_base * np.random.uniform(0.05, 0.1) 
                for _ in range(4)
            ],
            "free_cash_flow": [
                revenue_base * np.random.uniform(0.05, 0.2) 
                for _ in range(4)
            ],
            "dividends_paid": [
                -revenue_base * np.random.uniform(0.01, 0.05) 
                for _ in range(4)
            ],
            "net_borrowings": [
                revenue_base * np.random.uniform(-0.05, 0.05) 
                for _ in range(4)
            ]
        }
        
        # Key Ratios
        key_ratios = {
            "quarters": quarters,
            "gross_margin": [np.random.uniform(0.3, 0.6) for _ in range(4)],
            "operating_margin": [np.random.uniform(0.1, 0.3) for _ in range(4)],
            "net_margin": [np.random.uniform(0.05, 0.2) for _ in range(4)],
            "return_on_assets": [np.random.uniform(0.05, 0.15) for _ in range(4)],
            "return_on_equity": [np.random.uniform(0.1, 0.25) for _ in range(4)],
            "current_ratio": [np.random.uniform(1.0, 3.0) for _ in range(4)],
            "debt_to_equity": [np.random.uniform(0.5, 2.0) for _ in range(4)]
        }
        
        return {
            "ticker": ticker,
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow,
            "key_ratios": key_ratios,
            "currency": "USD",
            "updated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.exception(f"Error fetching financials for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e)
        }

async def fetch_company_profile(
    ticker: str,
    session: Optional[aiohttp.ClientSession] = None
) -> Dict[str, Any]:
    """
    Fetch company profile information.
    
    Args:
        ticker: Stock ticker symbol
        session: Aiohttp client session
        
    Returns:
        Dictionary with company profile data
    """
    try:
        # In a production environment, this would fetch from an external API
        # For this implementation, we'll generate mock data
        
        # Get basic info
        basic_info = await get_ticker_info(ticker, session)
        
        # Generate a deterministic "random" seed based on ticker
        seed = sum(ord(c) for c in ticker)
        np.random.seed(seed)
        
        # Company descriptions
        descriptions = [
            f"{basic_info['name']} is a leading provider of {basic_info['industry']} solutions, serving clients worldwide.",
            f"{basic_info['name']} operates in the {basic_info['sector']} sector, specializing in {basic_info['industry']} products and services.",
            f"Founded as a pioneer in the {basic_info['industry']} space, {basic_info['name']} has established itself as an industry leader.",
            f"{basic_info['name']} is dedicated to innovation in {basic_info['sector']}, with a focus on sustainable growth.",
            f"As a global leader in {basic_info['industry']}, {basic_info['name']} serves customers across {np.random.randint(20, 100)} countries."
        ]
        
        # Random founding year between 1950 and 2010
        founding_year = np.random.randint(1950, 2010)
        
        # CEO names
        first_names = ["John", "Sarah", "Michael", "Emma", "David", "Lisa", "Robert", "Linda", "William", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Brown", "Taylor", "Miller", "Wilson", "Moore", "Anderson", "Thomas", "Jackson"]
        ceo_name = f"{np.random.choice(first_names)} {np.random.choice(last_names)}"
        
        return {
            **basic_info,
            "description": np.random.choice(descriptions),
            "founded": founding_year,
            "headquarters": f"{np.random.choice(['New York', 'San Francisco', 'Chicago', 'Boston', 'Seattle'])}, {basic_info['country']}",
            "ceo": ceo_name,
            "employees": np.random.randint(100, 100000),
            "products": [f"Product {i+1}" for i in range(np.random.randint(3, 8))],
            "competitors": [f"COMP{i+1}" for i in range(np.random.randint(3, 6))],
            "website": f"https://www.{ticker.lower()}.com"
        }
    
    except Exception as e:
        logger.exception(f"Error fetching company profile for {ticker}: {e}")
        return {
            "ticker": ticker,
            "name": ticker.upper(),
            "error": str(e)
        }

def _get_cached_data(ticker: str, period: str) -> Optional[pd.DataFrame]:
    """
    Get data from cache if available and not expired.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period
        
    Returns:
        DataFrame if cached data exists and is valid, None otherwise
    """
    # In a real implementation, this would check Redis or file cache
    cache_file = f"cache/stock_data/{ticker}_{period}.parquet"
    
    try:
        if os.path.exists(cache_file):
            # Check if cache is expired
            modified_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - modified_time < 3600:  # 1 hour expiry
                return pd.read_parquet(cache_file)
    except Exception:
        pass
    
    return None

def _cache_data(ticker: str, period: str, df: pd.DataFrame) -> None:
    """
    Cache data for future use.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period
        df: DataFrame to cache
    """
    # In a real implementation, this would store in Redis or file cache
    cache_dir = "cache/stock_data"
    
    try:
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = f"{cache_dir}/{ticker}_{period}.parquet"
        df.to_parquet(cache_file, index=False)
    except Exception:
        pass

def _generate_mock_stock_data(ticker: str, period: str) -> pd.DataFrame:
    """
    Generate mock stock data for demonstration.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period
        
    Returns:
        DataFrame with mock price data
    """
    # Determine number of days based on period
    days_map = {
        "1d": 1,
        "5d": 5,
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "2y": 365*2,
        "5y": 365*5,
        "max": 365*10
    }
    days = days_map.get(period, 365)
    
    # Generate dates
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days)]
    dates.reverse()  # Oldest to newest
    
    # Filter for business days (rough approximation)
    dates = [date for date in dates if date.weekday() < 5]
    
    # Generate a deterministic "random" seed based on ticker
    seed = sum(ord(c) for c in ticker)
    np.random.seed(seed)
    
    # Generate a starting price (use ticker's first char ascii value for variety)
    base_price = ord(ticker[0].upper()) * 2 + 50
    
    # Add some randomness
    base_price = base_price * (1 + np.random.uniform(-0.1, 0.1))
    
    # Generate price data with a trend based on ticker
    trend = 0.0002 * (ord(ticker[0].upper()) % 10 - 5)  # -0.001 to 0.001
    volatility = 0.01 + 0.01 * (ord(ticker[0].lower()) % 5)  # 0.01 to 0.05
    
    prices = [base_price]
    for i in range(1, len(dates)):
        # Random walk with drift
        change = trend + np.random.normal(0, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    # Generate OHLCV data
    df = pd.DataFrame()
    df["date"] = dates
    df["ticker"] = ticker
    df["close"] = prices
    
    # Open is previous day's close with some noise
    df["open"] = df["close"].shift(1) * (1 + np.random.normal(0, 0.002, size=len(df)))
    df.loc[0, "open"] = df.loc[0, "close"] * (1 - 0.002)  # First day
    
    # High is max of open/close plus some noise
    df["high"] = df[["open", "close"]].max(axis=1) * (1 + np.abs(np.random.normal(0, 0.005, size=len(df))))
    
    # Low is min of open/close minus some noise
    df["low"] = df[["open", "close"]].min(axis=1) * (1 - np.abs(np.random.normal(0, 0.005, size=len(df))))
    
    # Volume varies with price volatility
    price_changes = np.abs(df["close"].pct_change())
    df["volume"] = np.random.randint(100000, 1000000, size=len(df)) * (1 + 5 * price_changes)
    df["volume"] = df["volume"].fillna(df["volume"].mean()).astype(int)
    
    # Adjusted close same as close for this example
    df["adjusted_close"] = df["close"]
    
    return df