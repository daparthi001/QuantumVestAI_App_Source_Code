"""Real-time market data WebSocket service."""

from __future__ import annotations

import asyncio
import random
from typing import Dict, Optional, Tuple

import requests

from .manager import ConnectionManager


class YahooFinanceClient:
    """Client for retrieving market data from Yahoo Finance.

    The implementation is intentionally lightweight; in production a more
    sophisticated client would likely be used.  The methods are synchronous so
    they can be easily mocked during tests.
    """

    base_url = "https://query1.finance.yahoo.com/v7/finance/quote"

    def fetch_price(self, symbol: str) -> float:
        """Return the latest market price for ``symbol``."""
        url = f"{self.base_url}?symbols={symbol}"
        resp = requests.get(url, timeout=5)
        data = resp.json()["quoteResponse"]["result"]
        if not data:
            raise ValueError(f"unknown symbol: {symbol}")
        return float(data[0]["regularMarketPrice"])

    # In a real implementation these would call dedicated services.  For the
    # purposes of this repository they are simple deterministic helpers so the
    # behaviour can be tested without external dependencies.
    def forecast(self, price: float) -> float:
        """Naive price forecast used as a placeholder."""
        return price * 1.01

    def sentiment(self, price: float) -> str:
        """Return a trivial sentiment estimate."""
        return "positive" if price >= 0 else "neutral"

    def fetch(self, symbol: str) -> Dict[str, object]:
        price = self.fetch_price(symbol)
        return {
            "price": price,
            "forecast": self.forecast(price),
            "sentiment": self.sentiment(price),
        }


class MarketWebSocket:
    """Background task that streams price, forecast and sentiment."""

    def __init__(
        self,
        manager: Optional[ConnectionManager] = None,
        client: Optional[YahooFinanceClient] = None,
    ) -> None:
        self.manager = manager or ConnectionManager()
        self.client = client or YahooFinanceClient()

    async def stream(
        self,
        symbol: str,
        interval_range: Tuple[float, float] = (2.0, 10.0),
        iterations: Optional[int] = None,
    ) -> None:
        """Continuously broadcast updates for ``symbol``.

        Parameters
        ----------
        symbol:
            Ticker symbol to broadcast.
        interval_range:
            Tuple containing the min and max delay (in seconds) between
            updates. A random value within this range is chosen for each
            iteration.
        iterations:
            Optional number of iterations.  ``None`` means run forever.  This is
            primarily useful for testing.
        """

        count = 0
        while True:
            payload = self.client.fetch(symbol)
            await self.manager.broadcast_stock_update(symbol, payload)
            count += 1
            if iterations is not None and count >= iterations:
                break
            delay = random.uniform(*interval_range)
            await asyncio.sleep(delay)
