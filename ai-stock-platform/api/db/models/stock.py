from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base import Base
from db.models.associations import user_watchlist, user_portfolio

class Stock(Base):
    """Stock model for basic stock information."""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True)
    name = Column(String)
    exchange = Column(String)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Latest price data
    last_price = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Predictability metrics
    predictability_score = Column(Float, nullable=True)
    volatility_score = Column(Float, nullable=True)
    trend_score = Column(Float, nullable=True)
    volume_score = Column(Float, nullable=True)
    
    # Relationships
    watched_by = relationship("User", secondary=user_watchlist, back_populates="watchlist")
    price_history = relationship("StockPrice", back_populates="stock")
    alerts = relationship("Alert", back_populates="stock")
    
    def __repr__(self):
        return f"<Stock {self.ticker}>"

class StockPrice(Base):
    """Historical stock price data."""
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"))
    date = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(Integer)
    
    # Relationships
    stock = relationship("Stock", back_populates="price_history")
    
    def __repr__(self):
        return f"<StockPrice {self.stock.ticker} {self.date.date()}>"

class Alert(Base):
    """Price alerts for stocks."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"))
    
    price = Column(Float)
    direction = Column(String)  # above, below
    
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    stock = relationship("Stock", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert {self.user.username} {self.stock.ticker} {self.direction} {self.price}>"