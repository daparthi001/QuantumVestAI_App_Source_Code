import logging
from datetime import datetime
from typing import List, Optional, Type

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

try:  # Lazy import so tests can inject models without triggering DB setup
    from db.models.stock import Stock, StockPrice
except Exception:  # pragma: no cover - allow tests to provide mocks
    Stock = None  # type: ignore
    StockPrice = None  # type: ignore

logger = logging.getLogger(__name__)


class PredictionDataAgent:
    """Fetch price data from external sources and store in the database."""

    def __init__(
        self,
        db: Session,
        symbols: List[str],
        stock_model: Optional[Type] = None,
        price_model: Optional[Type] = None,
    ) -> None:
        self.db = db
        self.symbols = symbols
        # Allow dependency injection of models for easier testing
        self.Stock = stock_model or Stock
        self.StockPrice = price_model or StockPrice

    def fetch_prices(self, symbol: str, days: int = 1) -> pd.DataFrame:
        """Retrieve recent historical prices using yfinance."""
        try:
            df = yf.download(symbol, period=f"{days}d", interval="1d", progress=False)
            df = df.reset_index()
            df.rename(
                columns={
                    "Date": "date",
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Adj Close": "adjusted_close",
                    "Volume": "volume",
                },
                inplace=True,
            )
            df["date"] = pd.to_datetime(df["date"])
            return df
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Failed to fetch prices for %s: %s", symbol, exc)
            return pd.DataFrame()

    def store_prices(self, symbol: str, df: pd.DataFrame) -> None:
        """Insert fetched prices into the database."""
        if df.empty:
            return

        stock = self.db.query(self.Stock).filter_by(ticker=symbol).first()
        if not stock:
            stock = self.Stock(ticker=symbol, name=symbol, exchange="")
            self.db.add(stock)
            self.db.commit()
            self.db.refresh(stock)

        for _, row in df.iterrows():
            price = (
                self.db.query(self.StockPrice)
                .filter_by(stock_id=stock.id, date=row["date"])
                .first()
            )
            if price:
                price.open = row["open"]
                price.high = row["high"]
                price.low = row["low"]
                price.close = row["close"]
                price.adjusted_close = row["adjusted_close"]
                price.volume = int(row["volume"])
            else:
                price = self.StockPrice(
                    stock_id=stock.id,
                    date=row["date"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    adjusted_close=row["adjusted_close"],
                    volume=int(row["volume"]),
                )
                self.db.add(price)

        stock.last_price = float(df.iloc[-1]["close"])
        stock.last_updated = datetime.utcnow()
        self.db.commit()

    def update_symbols(self, days: int = 1) -> None:
        """Fetch and store data for all configured symbols."""
        for symbol in self.symbols:
            df = self.fetch_prices(symbol, days=days)
            self.store_prices(symbol, df)
