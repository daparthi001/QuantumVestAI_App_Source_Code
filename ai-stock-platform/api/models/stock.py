"""
Stock Models Implementation
Created: 2025-05-19 03:44:39
Author: daparthi001
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from api.models.base import ModelBase, TimestampMixin, UserMixin

class StockExchange(enum.Enum):
    """Stock exchange enumeration"""
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    AMEX = "AMEX"
    OTC = "OTC"

class Stock(ModelBase, TimestampMixin, UserMixin):
    """Stock model"""
    __tablename__ = "stocks"

    # Basic information
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    exchange = Column(Enum(StockExchange), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    
    # Current data
    current_price = Column(Float)
    volume = Column(Integer)
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    dividend_yield = Column(Float)
    
    # Price data
    day_high = Column(Float)
    day_low = Column(Float)
    fifty_two_week_high = Column(Float)
    fifty_two_week_low = Column(Float)
    
    # Metadata
    description = Column(String(1000))
    website = Column(String(255))
    ceo = Column(String(100))
    employees = Column(Integer)
    headquarters = Column(String(255))
    
    # Relationships
    prices = relationship("StockPrice", back_populates="stock", cascade="all, delete-orphan")
    fundamentals = relationship("StockFundamentals", back_populates="stock", cascade="all, delete-orphan")
    indicators = relationship("TechnicalIndicator", back_populates="stock", cascade="all, delete-orphan")

class StockPrice(ModelBase, TimestampMixin):
    """Stock price model"""
    __tablename__ = "stock_prices"

    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="prices")

class StockFundamentals(ModelBase, TimestampMixin):
    """Stock fundamentals model"""
    __tablename__ = "stock_fundamentals"

    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Income Statement
    revenue = Column(Float)
    net_income = Column(Float)
    eps = Column(Float)
    
    # Balance Sheet
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)
    
    # Cash Flow
    operating_cash_flow = Column(Float)
    investing_cash_flow = Column(Float)
    financing_cash_flow = Column(Float)
    
    # Ratios
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    debt_to_equity = Column(Float)
    
    # Additional Data
    raw_data = Column(JSON)
    
    # Relationships
    stock = relationship("Stock", back_populates="fundamentals")

class TechnicalIndicator(ModelBase, TimestampMixin):
    """Technical indicator model"""
    __tablename__ = "technical_indicators"

    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Moving Averages
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    
    # Momentum Indicators
    rsi_14 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_hist = Column(Float)
    
    # Volatility Indicators
    bollinger_upper = Column(Float)
    bollinger_middle = Column(Float)
    bollinger_lower = Column(Float)
    atr = Column(Float)
    
    # Volume Indicators
    obv = Column(Float)
    
    # Relationships
    stock = relationship("Stock", back_populates="indicators")