"""Market data websocket utilities.

This module provides a lightweight service that periodically fetches mock
market data and broadcasts the results to any connected websocket clients.
It relies on the existing :class:`ConnectionManager` to handle subscriptions
and client management.  The service is intentionally simple so it can operate
in the test environment without external dependencies or real market feeds.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from .manager import ConnectionManager
from utils.market_data import MarketDataClient


class MarketWebSocketService:
    """Background broadcaster for live stock data."""

    def __init__(
        self,
        manager: Optional[ConnectionManager] = None,
        client: Optional[MarketDataClient] = None,
    ) -> None:
        self.manager = manager or ConnectionManager()
        self.client = client or MarketDataClient()

    async def stream(self, symbol: str, interval: float = 1.0) -> None:
        """Continuously fetch data for ``symbol`` and broadcast to subscribers.

        Parameters
        ----------
        symbol: str
            Stock ticker symbol to broadcast.
        interval: float, optional
            Delay between fetches in seconds.  Defaults to ``1``.
        """

        while True:
            data = self.client.get_data(symbol)
            await self.manager.broadcast_stock_update(symbol, data)
            await asyncio.sleep(interval)
