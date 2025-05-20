"""
Stock data service
Created: 2025-05-19 03:29:10
Author: daparthi001
"""
import aiohttp
import asyncio
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from api.models.stock import Stock, WatchList
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.ALPHA_VANTAGE_API_KEY.get_secret_value()
        self.base_url = "https://www.alphavantage.co/query"

    async def get_stock_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch real-time stock data from Alpha Vantage"""
        async with aiohttp.ClientSession() as session:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            try:
                async with session.get(self.base_url, params=params) as response:
                    data = await response.json()
                    if "Global Quote" in data:
                        return data["Global Quote"]
                    return None
            except Exception as e:
                logger.error(f"Error fetching stock data for {symbol}: {str(e)}")
                return None

    async def update_stock_data(self, symbol: str) -> Optional[Stock]:
        """Update stock data in database"""
        data = await self.get_stock_data(symbol)
        if not data:
            return None

        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            stock = Stock(symbol=symbol)

        stock.current_price = float(data.get("05. price", 0))
        stock.high_24h = float(data.get("03. high", 0))
        stock.low_24h = float(data.get("04. low", 0))
        stock.volume_24h = float(data.get("06. volume", 0))
        
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock

    def get_user_watchlist(self, user_id: int) -> List[Stock]:
        """Get user's watchlist"""
        return (self.db.query(Stock)
                .join(WatchList)
                .filter(WatchList.user_id == user_id)
                .all())

    def add_to_watchlist(self, user_id: int, symbol: str) -> bool:
        """Add stock to user's watchlist"""
        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            return False

        if not self.db.query(WatchList).filter(
            WatchList.user_id == user_id,
            WatchList.stock_id == stock.id
        ).first():
            watchlist_item = WatchList(user_id=user_id, stock_id=stock.id)
            self.db.add(watchlist_item)
            self.db.commit()
        return True

    def remove_from_watchlist(self, user_id: int, symbol: str) -> bool:
        """Remove stock from user's watchlist"""
        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            return False

        watchlist_item = self.db.query(WatchList).filter(
            WatchList.user_id == user_id,
            WatchList.stock_id == stock.id
        ).first()
        
        if watchlist_item:
            self.db.delete(watchlist_item)
            self.db.commit()
            return True
        return False