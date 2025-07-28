import logging
from datetime import datetime
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import yfinance as yf
except Exception:  # pragma: no cover - optional dependency
    yf = None

# Basic constants mirroring UI service
MARKET_INDICES = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Russell 2000": "^RUT",
    "VIX": "^VIX",
}

SECTOR_ETFS = {
    "Technology": "VGT",
    "Healthcare": "VHT",
    "Financials": "VFH",
    "Consumer Discretionary": "VCR",
    "Consumer Staples": "VDC",
    "Energy": "VDE",
    "Industrials": "VIS",
    "Utilities": "VPU",
    "Materials": "VAW",
    "Real Estate": "VNQ",
    "Communication Services": "VOX",
}

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

logger = logging.getLogger(__name__)

class MarketOverviewService:
    """Simple market overview service using yfinance when available."""

    @staticmethod
    def _fetch_info(symbol: str) -> Dict[str, Any]:
        """Fetch basic quote info for a symbol."""
        if yf is None:
            # Return mock values if yfinance is unavailable
            return {
                "symbol": symbol,
                "price": 0.0,
                "change": 0.0,
                "change_percent": 0.0,
                "volume": 0,
                "name": symbol,
            }
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "symbol": symbol,
                "price": info.get("regularMarketPrice", 0.0),
                "change": info.get("regularMarketChange", 0.0),
                "change_percent": info.get("regularMarketChangePercent", 0.0),
                "volume": info.get("regularMarketVolume", 0),
                "name": info.get("shortName", symbol),
            }
        except Exception as exc:  # pragma: no cover - network errors
            logger.warning("Failed to fetch info for %s: %s", symbol, exc)
            return {
                "symbol": symbol,
                "price": 0.0,
                "change": 0.0,
                "change_percent": 0.0,
                "volume": 0,
                "name": symbol,
            }

    @classmethod
    def get_market_overview(cls) -> Dict[str, Any]:
        """Return market overview including indices and sector performance."""
        overview = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "indices": [],
            "sectors": [],
            "market_sentiment": "neutral",
            "volatility_index": 0.0,
        }

        # Fetch indices
        indices = []
        for name, sym in MARKET_INDICES.items():
            data = cls._fetch_info(sym)
            indices.append({
                "name": name,
                "value": data.get("price", 0.0),
                "change_percent": data.get("change_percent", 0.0),
            })
            if sym == "^VIX":
                overview["volatility_index"] = data.get("price", 0.0)
        overview["indices"] = indices

        # Derive simple sentiment from average change
        if indices:
            avg_change = sum(i.get("change_percent", 0.0) for i in indices) / len(indices)
            if avg_change > 0.2:
                overview["market_sentiment"] = "bullish"
            elif avg_change < -0.2:
                overview["market_sentiment"] = "bearish"
            else:
                overview["market_sentiment"] = "neutral"

        # Fetch sectors
        sectors = []
        for sector, sym in SECTOR_ETFS.items():
            data = cls._fetch_info(sym)
            sectors.append({
                "name": sector,
                "change_percent": data.get("change_percent", 0.0),
            })
        overview["sectors"] = sectors
        return overview

    @classmethod
    def get_top_movers(cls) -> Dict[str, List[Dict[str, Any]]]:
        """Return simple top gainers and losers from a sample list."""
        tickers = DEFAULT_TICKERS + ["GOOGL", "NFLX", "META", "NVDA"]
        results: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(cls._fetch_info, t): t for t in tickers}
            for fut in as_completed(futures):
                results.append(fut.result())

        gainers = sorted(results, key=lambda x: x.get("change_percent", 0.0), reverse=True)[:5]
        losers = sorted(results, key=lambda x: x.get("change_percent", 0.0))[:5]
        return {"gainers": gainers, "losers": losers}
