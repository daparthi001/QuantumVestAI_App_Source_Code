"""QuantumVestAI Data API using Yahoo Finance"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
import logging
from datetime import datetime
from urllib.parse import urlencode
import time


router = APIRouter(prefix="/api/ai", tags=["ai-data"])
logger = logging.getLogger(__name__)

BASE_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart"
SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"

# Simple in-memory cache to avoid hitting Yahoo Finance too often
CACHE_TTL = 60  # seconds
_cache: dict[str, tuple[float, dict]] = {}

def _cache_key(url: str, params: dict | None) -> str:
    if not params:
        return url
    return f"{url}?{urlencode(params, doseq=True)}"

async def fetch_json(url: str, params: dict | None = None):
    """Helper to fetch JSON data from a remote endpoint with caching."""
    key = _cache_key(url, params)
    now = time.time()
    if key in _cache and now - _cache[key][0] < CACHE_TTL:
        return _cache[key][1]

    async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "QuantumVestAI/1.0"}) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        _cache[key] = (now, data)
        return data


@router.get("/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Return intraday price data for a symbol."""
    try:
        data = await fetch_json(f"{BASE_CHART_URL}/{symbol}", params={"range": "1d", "interval": "1m"})
        chart = data.get("chart", {}).get("result")
        if not chart:
            raise HTTPException(status_code=404, detail="Data not found")
        result = chart[0]
        timestamps = result.get("timestamp", [])
        prices = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        volume = result.get("indicators", {}).get("quote", [{}])[0].get("volume", [])
        return {
            "symbol": symbol.upper(),
            "timestamps": timestamps,
            "prices": prices,
            "volume": volume,
            "timestamp": datetime.utcnow().isoformat()
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching market data for {symbol}: {e}")
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Upstream rate limited")

        raise HTTPException(status_code=502, detail="Upstream error")
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data")

@router.get("/technical-data/{symbol}")
async def get_technical_data(symbol: str):
    """Return simple technical indicators (SMA and EMA)"""
    try:
        data = await fetch_json(f"{BASE_CHART_URL}/{symbol}", params={"range": "1mo", "interval": "1d"})
        chart = data.get("chart", {}).get("result")
        if not chart:
            raise HTTPException(status_code=404, detail="Data not found")
        closes = chart[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])
        if not closes:
            raise HTTPException(status_code=404, detail="No close prices")
        sma = sum(closes[-20:]) / min(len(closes), 20)
        ema = closes[-1]
        alpha = 2 / (min(len(closes), 20) + 1)
        for price in closes[-20:]:
            ema = alpha * price + (1 - alpha) * ema
        return {
            "symbol": symbol.upper(),
            "sma": sma,
            "ema": ema,
            "timestamp": datetime.utcnow().isoformat()
        }
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching technical data for {symbol}: {e}")
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Upstream rate limited")

        raise HTTPException(status_code=502, detail="Upstream error")
    except Exception as e:
        logger.error(f"Error fetching technical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data")

@router.get("/news/{symbol}")
async def get_news(symbol: str):
    """Return news search results for a symbol."""
    try:
        data = await fetch_json(SEARCH_URL, params={"q": symbol, "newsCount": 5})
        news = data.get("news", [])
        return {"symbol": symbol.upper(), "news": news, "timestamp": datetime.utcnow().isoformat()}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching news for {symbol}: {e}")
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Upstream rate limited")

        raise HTTPException(status_code=502, detail="Upstream error")
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data")

@router.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """Return placeholder sentiment score using news headlines."""
    try:
        data = await fetch_json(SEARCH_URL, params={"q": symbol, "newsCount": 20})
        headlines = [n.get("title", "") for n in data.get("news", [])]
        score = sum(1 for h in headlines if "up" in h.lower()) - sum(1 for h in headlines if "down" in h.lower())
        return {"symbol": symbol.upper(), "score": score, "timestamp": datetime.utcnow().isoformat()}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching sentiment for {symbol}: {e}")
        if e.response.status_code == 429:
            raise HTTPException(status_code=429, detail="Upstream rate limited")

        raise HTTPException(status_code=502, detail="Upstream error")
    except Exception as e:
        logger.error(f"Error fetching sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch data")
