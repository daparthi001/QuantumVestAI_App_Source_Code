from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base_class import Base


class WatchlistStock(Base):
    __tablename__ = "watchlist_stocks"
    __table_args__ = {"extend_existing": True}

    watchlist_id = Column(Integer, ForeignKey("watchlists.id", ondelete="CASCADE"), primary_key=True)
    stock_ticker = Column(String(20), ForeignKey("stocks.ticker", ondelete="CASCADE"), primary_key=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    watchlist = relationship("Watchlist", back_populates="stocks")
    stock = relationship("Stock", back_populates="watchlists")
