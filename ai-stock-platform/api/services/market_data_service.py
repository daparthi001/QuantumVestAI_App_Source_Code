"""
Real-time Market Data Service
Created: 2025-05-19 04:35:05
Author: daparthi001
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
import redis
import json
from fastapi import WebSocket
from api.core.config import settings
from api.utils.websocket_manager import WebSocketManager

class MarketDataService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        self.ws_manager = WebSocketManager()
        self.subscriptions: Dict[str, set] = {}
        self.last_prices: Dict[str, float] = {}
        
        # Initialize connection
        asyncio.create_task(self._initialize_market_data_stream())

    async def _initialize_market_data_stream(self):
        """Initialize WebSocket connection to market data provider"""
        while True:
            try:
                async with aiohttp.ClientWebSocket() as ws:
                    await self._authenticate_stream(ws)
                    await self._handle_market_data_stream(ws)
            except Exception as e:
                print(f"Market data stream error: {e}")
                await asyncio.sleep(5)  # Reconnection delay

    async def _authenticate_stream(self, ws: aiohttp.ClientWebSocket):
        """Authenticate with market data provider"""
        auth_message = {
            "type": "auth",
            "api_key": settings.MARKET_DATA_API_KEY
        }
        await ws.send_json(auth_message)
        response = await ws.receive_json()
        if response.get("status") != "authenticated":
            raise Exception("Failed to authenticate market data stream")

    async def _handle_market_data_stream(self, ws: aiohttp.ClientWebSocket):
        """Handle incoming market data stream"""
        async for message in ws:
            if message.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(message.data)
                await self._process_market_data(data)
            elif message.type == aiohttp.WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")

    async def _process_market_data(self, data: Dict):
        """Process incoming market data and update cache"""
        try:
            symbol = data["symbol"]
            price = float(data["price"])
            timestamp = datetime.fromtimestamp(data["timestamp"])

            # Update cache
            self.last_prices[symbol] = price
            cache_key = f"market_data:{symbol}"
            cache_data = {
                "price": price,
                "timestamp": timestamp.isoformat(),
                "volume": data.get("volume", 0),
                "high": data.get("high", price),
                "low": data.get("low", price)
            }
            self.redis_client.setex(
                cache_key,
                settings.MARKET_DATA_CACHE_TTL,
                json.dumps(cache_data)
            )

            # Notify subscribers
            if symbol in self.subscriptions:
                await self._notify_subscribers(symbol, cache_data)

        except Exception as e:
            print(f"Error processing market data: {e}")

    async def _notify_subscribers(self, symbol: str, data: Dict):
        """Notify WebSocket subscribers of price updates"""
        message = {
            "type": "price_update",
            "symbol": symbol,
            "data": data
        }
        for connection_id in self.subscriptions[symbol]:
            await self.ws_manager.send_personal_message(
                connection_id,
                json.dumps(message)
            )

    async def subscribe_to_symbol(self, symbol: str, connection_id: str):
        """Subscribe to real-time updates for a symbol"""
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = set()
            # Subscribe to market data provider
            await self._subscribe_to_market_data(symbol)
        
        self.subscriptions[symbol].add(connection_id)

    async def unsubscribe_from_symbol(self, symbol: str, connection_id: str):
        """Unsubscribe from real-time updates for a symbol"""
        if symbol in self.subscriptions:
            self.subscriptions[symbol].discard(connection_id)
            if not self.subscriptions[symbol]:
                del self.subscriptions[symbol]
                # Unsubscribe from market data provider
                await self._unsubscribe_from_market_data(symbol)

    async def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        # Try cache first
        cache_key = f"market_data:{symbol}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            data = json.loads(cached_data)
            return float(data["price"])
            
        # Fallback to API call
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.MARKET_DATA_API_URL}/quote/{symbol}",
                headers={"Authorization": f"Bearer {settings.MARKET_DATA_API_KEY}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data["price"])
                else:
                    raise Exception(f"Failed to get price for {symbol}")

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = "1d"
    ) -> List[Dict]:
        """Get historical price data for a symbol"""
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=365)

        cache_key = f"historical:{symbol}:{start_date.date()}:{end_date.date()}:{interval}"
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.MARKET_DATA_API_URL}/historical/{symbol}",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "interval": interval
                },
                headers={"Authorization": f"Bearer {settings.MARKET_DATA_API_KEY}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache the results
                    self.redis_client.setex(
                        cache_key,
                        settings.HISTORICAL_DATA_CACHE_TTL,
                        json.dumps(data)
                    )
                    return data
                else:
                    raise Exception(f"Failed to get historical data for {symbol}")

    async def get_market_news(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get market news for a symbol or general market news"""
        cache_key = f"news:{symbol if symbol else 'market'}"
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        async with aiohttp.ClientSession() as session:
            url = f"{settings.MARKET_DATA_API_URL}/news"
            if symbol:
                url += f"/{symbol}"
                
            async with session.get(
                url,
                headers={"Authorization": f"Bearer {settings.MARKET_DATA_API_KEY}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache the results
                    self.redis_client.setex(
                        cache_key,
                        settings.NEWS_CACHE_TTL,
                        json.dumps(data)
                    )
                    return data
                else:
                    raise Exception(f"Failed to get news data")

    async def get_market_indicators(self) -> Dict:
        """Get market-wide indicators"""
        cache_key = "market:indicators"
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.MARKET_DATA_API_URL}/indicators",
                headers={"Authorization": f"Bearer {settings.MARKET_DATA_API_KEY}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache the results
                    self.redis_client.setex(
                        cache_key,
                        settings.INDICATORS_CACHE_TTL,
                        json.dumps(data)
                    )
                    return data
                else:
                    raise Exception("Failed to get market indicators")
