from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.db.base_class import Base


class Stock(Base):
    __tablename__ = "stocks"

    ticker = Column(String(20), primary_key=True)
    company_name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(100))
    predictability_score = Column(Numeric(5, 2))
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    forecasts = relationship("StockForecast", back_populates="stock", cascade="all, delete-orphan")
    watchlists = relationship("WatchlistStock", back_populates="stock")