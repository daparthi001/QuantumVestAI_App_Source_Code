"""
Stock Service Implementation
Created: 2025-05-19 03:45:54
Author: daparthi001
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from fastapi import HTTPException

from api.models.stock import Stock, StockPrice, StockFundamentals, TechnicalIndicator
from api.services.base import BaseService
from api.core.config import settings
from api.core.cache import cache

class StockService(BaseService[Stock]):
    """Service for stock-related operations"""
    
    def __init__(self, db: Session):
        super().__init__(Stock, db)
        self.cache_prefix = "stock:"
        self.cache_ttl = 300  # 5 minutes
    
    async def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock information with caching"""
        cache_key = f"{self.cache_prefix}info:{symbol}"
        
        # Try cache first
        if cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Get data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Process and validate data
            stock_info = {
                "symbol": symbol,
                "name": info.get("longName", ""),
                "exchange": info.get("exchange", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "current_price": info.get("regularMarketPrice", 0),
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "day_high": info.get("dayHigh", 0),
                "day_low": info.get("dayLow", 0),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
                "description": info.get("longBusinessSummary", ""),
                "website": info.get("website", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            if cache:
                cache.set(cache_key, stock_info, ttl_seconds=self.cache_ttl)
            
            return stock_info
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch stock information: {str(e)}"
            )
    
    async def get_historical_prices(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """Get historical price data"""
        if not start_date:
            start_date = datetime.now() - timedelta(days=365)
        if not end_date:
            end_date = datetime.now()
        
        cache_key = f"{self.cache_prefix}prices:{symbol}:{start_date.date()}:{end_date.date()}:{interval}"
        
        # Try cache first
        if cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data
        
        try:
            # Get data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            # Process data
            prices = []
            for index, row in df.iterrows():
                price_data = {
                    "date": index.isoformat(),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"],
                    "adjusted_close": row["Close"]
                }
                prices.append(price_data)
            
            # Cache the result
            if cache:
                cache.set(cache_key, prices, ttl_seconds=self.cache_ttl)
            
            return prices
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch historical prices: {str(e)}"
            )
    
    async def calculate_technical_indicators(
        self,
        symbol: str,
        indicators: List[str] = None
    ) -> Dict[str, Any]:
        """Calculate technical indicators"""
        if not indicators:
            indicators = ["sma", "rsi", "macd", "bollinger"]
        
        try:
            # Get historical data
            prices = await self.get_historical_prices(symbol)
            df = pd.DataFrame(prices)
            
            result = {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "indicators": {}
            }
            
            # Calculate indicators
            if "sma" in indicators:
                result["indicators"]["sma"] = {
                    "sma_20": self._calculate_sma(df, 20),
                    "sma_50": self._calculate_sma(df, 50),
                    "sma_200": self._calculate_sma(df, 200)
                }
            
            if "rsi" in indicators:
                result["indicators"]["rsi"] = self._calculate_rsi(df)
            
            if "macd" in indicators:
                result["indicators"]["macd"] = self._calculate_macd(df)
            
            if "bollinger" in indicators:
                result["indicators"]["bollinger"] = self._calculate_bollinger_bands(df)
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to calculate indicators: {str(e)}"
            )
    
    def _calculate_sma(self, df: pd.DataFrame, period: int) -> float:
        """Calculate Simple Moving Average"""
        return df["close"].rolling(window=period).mean().iloc[-1]
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs.iloc[-1]))
    
    def _calculate_macd(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate MACD"""
        exp1 = df["close"].ewm(span=12, adjust=False).mean()
        exp2 = df["close"].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return {
            "macd": macd.iloc[-1],
            "signal": signal.iloc[-1],
            "histogram": macd.iloc[-1] - signal.iloc[-1]
        }
    
    def _calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        period: int = 20,
        num_std: int = 2
    ) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        sma = df["close"].rolling(window=period).mean()
        std = df["close"].rolling(window=period).std()
        return {
            "upper": sma.iloc[-1] + (std.iloc[-1] * num_std),
            "middle": sma.iloc[-1],
            "lower": sma.iloc[-1] - (std.iloc[-1] * num_std)
        }