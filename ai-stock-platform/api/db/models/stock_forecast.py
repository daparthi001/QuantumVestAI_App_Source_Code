# Register this model on the shared SQLAlchemy Base used by other models.
from db.base import Base, TimestampMixin
from sqlalchemy import (Column, Date, ForeignKey, Integer, Numeric, String,
                        UniqueConstraint)
from sqlalchemy.orm import relationship


class StockForecast(Base, TimestampMixin):
    __tablename__ = "stock_forecasts"
    __table_args__ = (UniqueConstraint('ticker', 'forecast_date', 'model_name'),
                      {"extend_existing": True})

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), ForeignKey("stocks.ticker"))
    forecast_date = Column(Date, nullable=False)
    model_name = Column(String(100), nullable=False)
    forecast_1d = Column(Numeric(10, 2))
    forecast_1w = Column(Numeric(10, 2))
    forecast_1m = Column(Numeric(10, 2))
    forecast_3m = Column(Numeric(10, 2))
    confidence_score = Column(Numeric(5, 2))

    # Unique constraint to prevent duplicate forecasts defined above

    # Relationships    stock = relationship("Stock", back_populates="forecasts")
