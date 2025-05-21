"""
Stock Models Module
Created: 2025-05-19 03:27:22
Updated: 2025-05-21 15:48:25
Author: daparthi001
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base_class import Base
from db.models.mixins import TimestampMixin

class Stock(Base, TimestampMixin):
    """Stock market data model"""
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String)
    current_price = Column(Float)
    high_24h = Column(Float)
    low_24h = Column(Float)
    volume_24h = Column(Float)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    watchlists = relationship("WatchList", back_populates="stock")

class WatchList(Base, TimestampMixin):
    """User watchlist model"""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="watchlists")
    stock = relationship("Stock", back_populates="watchlists")