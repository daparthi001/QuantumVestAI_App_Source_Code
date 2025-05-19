"""
Stock Model
Created: 2025-05-19 04:05:44
Author: daparthi001
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.db.base import Base, TimestampMixin

class Stock(Base, TimestampMixin):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    sector = Column(String)
    market_cap = Column(Float)
    current_price = Column(Float)
    
    # Relationships
    prices = relationship("StockPrice", back_populates="stock")

class StockPrice(Base, TimestampMixin):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    date = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    # Relationship
    stock = relationship("Stock", back_populates="prices")