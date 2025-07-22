"""
Market Data Client Stub
Created: 2025-07-22
Author: QuantumVestAI Auto-Fix
"""

import os
import requests
import json
from datetime import datetime, timedelta

# Expose the API key for other modules if needed
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

class MarketDataClient:
    def __init__(self):
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def get_data(self, symbol: str, interval: str = "1min", **kwargs):
        """
        Fetch market data for a given symbol and interval from Alpha Vantage (stub: returns static data if API key is demo).
        """
        if self.api_key == "demo":
            # Return static stub data for demo
            return {
                "symbol": symbol,
                "interval": interval,
                "data": [
                    {"timestamp": datetime.utcnow().isoformat(), "price": 100.0}
                ],
                "source": "stub"
            }
        # Example real API call (uncomment and handle errors in production)
        # params = {
        #     "function": "TIME_SERIES_INTRADAY",
        #     "symbol": symbol,
        #     "interval": interval,
        #     "apikey": self.api_key
        # }
        # response = requests.get(self.base_url, params=params)
        # return response.json()
        return {
            "symbol": symbol,
            "interval": interval,
            "data": [],
            "source": "stub"
        }

    def get_latest_price(self, symbol: str) -> float:
        """
        Return the latest price for a symbol (stub: always returns 100.0 for demo).
        """
        if self.api_key == "demo":
            return 100.0
        # Example real API call (uncomment in production)
        # data = self.get_data(symbol)
        # return float(data["data"][0]["price"])
        return 100.0

    def get_historical(self, symbol: str, start: str, end: str) -> list:
        """
        Return historical data for a symbol between start and end dates (stub: returns empty list for demo).
        """
        if self.api_key == "demo":
            return []
        # Example real API call (uncomment in production)
        # params = { ... }
        # response = requests.get(self.base_url, params=params)
        # return response.json()
        return []

def get_market_data(symbol: str, interval: str = "1min", **kwargs):
    """
    Fetch market data for a given symbol and interval (function version).
    """
    client = MarketDataClient()
    return client.get_data(symbol, interval, **kwargs)
