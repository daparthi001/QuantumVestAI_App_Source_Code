class MarketDataService:
    async def get_quote(self, symbol: str):
        """Return a dummy market quote for the given symbol."""
        return {"symbol": symbol, "bid": 100.0, "ask": 100.5, "last": 100.25}
