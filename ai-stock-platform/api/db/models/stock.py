"""
Stock Models Module
Created: 2025-05-21 17:22:14
Author: daparthi001
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from db.base import Base, TimestampMixin
from db.models.associations import user_watchlist, user_portfolio

class Stock(Base, TimestampMixin):
    """Stock model for basic stock information."""
    __tablename__ = "stocks"
    
    # Primary fields
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = Column(String, unique=True, index=True)
    name: Mapped[str] = Column(String)
    exchange: Mapped[str] = Column(String)
    sector: Mapped[Optional[str]] = Column(String, nullable=True)
    industry: Mapped[Optional[str]] = Column(String, nullable=True)
    country: Mapped[Optional[str]] = Column(String, nullable=True)
    
    # Latest price data
    last_price: Mapped[Optional[float]] = Column(Float, nullable=True)
    last_updated: Mapped[Optional[datetime]] = Column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now()
    )
    
    # Status
    is_active: Mapped[bool] = Column(Boolean, default=True)
    
    # Predictability metrics
    predictability_score: Mapped[Optional[float]] = Column(Float, nullable=True)
    volatility_score: Mapped[Optional[float]] = Column(Float, nullable=True)
    trend_score: Mapped[Optional[float]] = Column(Float, nullable=True)
    volume_score: Mapped[Optional[float]] = Column(Float, nullable=True)
    
    # Relationships
    watched_by: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_watchlist,
        back_populates="watchlist"
    )
    price_history: Mapped[List["StockPrice"]] = relationship(
        "StockPrice",
        back_populates="stock",
        cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="stock",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Stock {self.ticker}>"

class StockPrice(Base, TimestampMixin):
    """Historical stock price data."""
    __tablename__ = "stock_prices"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    stock_id: Mapped[int] = Column(
        Integer,
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=False
    )
    date: Mapped[datetime] = Column(DateTime(timezone=True), index=True)
    open: Mapped[float] = Column(Float, nullable=False)
    high: Mapped[float] = Column(Float, nullable=False)
    low: Mapped[float] = Column(Float, nullable=False)
    close: Mapped[float] = Column(Float, nullable=False)
    adjusted_close: Mapped[Optional[float]] = Column(Float, nullable=True)
    volume: Mapped[int] = Column(Integer, nullable=False)
    
    # Relationships
    stock: Mapped["Stock"] = relationship("Stock", back_populates="price_history")
    
    @property
    def price_change(self) -> float:
        """Calculate price change from open to close"""
        return self.close - self.open
    
    @property
    def price_change_percent(self) -> float:
        """Calculate percentage price change"""
        return (self.price_change / self.open) * 100 if self.open else 0
    
    def __repr__(self) -> str:
        return f"<StockPrice {self.stock.ticker} {self.date.date()}>"

class Alert(Base, TimestampMixin):
    """Price alerts for stocks."""
    __tablename__ = "alerts"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id: Mapped[int] = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    stock_id: Mapped[int] = Column(
        Integer,
        ForeignKey("stocks.id", ondelete="CASCADE"),
        nullable=False
    )
    
    price: Mapped[float] = Column(Float, nullable=False)
    direction: Mapped[str] = Column(String, nullable=False)  # above, below
    
    is_triggered: Mapped[bool] = Column(Boolean, default=False)
    triggered_at: Mapped[Optional[datetime]] = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="alerts")
    stock: Mapped["Stock"] = relationship("Stock", back_populates="alerts")
    
    def check_trigger(self, current_price: float) -> bool:
        """
        Check if alert should be triggered based on current price
        
        Args:
            current_price: The current stock price to check against
            
        Returns:
            bool: True if alert should be triggered, False otherwise
        """
        if not self.is_triggered:
            if self.direction == "above" and current_price >= self.price:
                self.trigger()
                return True
            elif self.direction == "below" and current_price <= self.price:
                self.trigger()
                return True
        return False
    
    def trigger(self) -> None:
        """Mark alert as triggered with current timestamp"""
        self.is_triggered = True
        self.triggered_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<Alert {self.user.username} {self.stock.ticker} {self.direction} {self.price}>"