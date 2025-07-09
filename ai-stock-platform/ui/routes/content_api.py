"""Content API routes providing demo data for the UI."""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/news")
async def get_news():
    """Return demo news articles."""
    now = datetime.utcnow()
    return [
        {
            "id": "1",
            "title": "Market Rally Continues as Tech Stocks Surge",
            "summary": "Technology stocks led market gains today as investors showed renewed confidence in the sector...",
            "url": "#",
            "source": "QuantumNews",
            "category": "market",
            "timestamp": (now).isoformat() + "Z",
            "tags": ["technology", "stocks", "market"],
            "sentiment": {"label": "POSITIVE", "score": 0.8},
            "views": 1250,
            "comments": 45,
            "likes": 89,
            "relevanceScore": 0.95,
        },
        {
            "id": "2",
            "title": "Federal Reserve Signals Potential Rate Changes",
            "summary": "Federal Reserve officials hinted at possible interest rate adjustments in upcoming meetings...",
            "url": "#",
            "source": "Reuters",
            "category": "economy",
            "timestamp": (now).isoformat() + "Z",
            "tags": ["federal-reserve", "interest-rates", "economy"],
            "sentiment": {"label": "NEUTRAL", "score": 0.1},
            "views": 2100,
            "comments": 78,
            "likes": 156,
            "relevanceScore": 0.87,
        },
        {
            "id": "3",
            "title": "Cryptocurrency Market Shows Mixed Signals",
            "summary": "Bitcoin and major altcoins display divergent patterns as regulatory clarity remains uncertain...",
            "url": "#",
            "source": "Bloomberg",
            "category": "crypto",
            "timestamp": (now).isoformat() + "Z",
            "tags": ["cryptocurrency", "bitcoin", "regulation"],
            "sentiment": {"label": "NEGATIVE", "score": -0.3},
            "views": 890,
            "comments": 23,
            "likes": 34,
            "relevanceScore": 0.72,
        },
    ]


@router.get("/trending")
async def get_trending_topics():
    """Return demo trending topics."""
    return [
        {"name": "AI Stocks", "count": "1.2K"},
        {"name": "Fed Policy", "count": "890"},
        {"name": "Crypto Regulation", "count": "654"},
        {"name": "Tech Earnings", "count": "432"},
        {"name": "Green Energy", "count": "289"},
    ]


@router.get("/market-movers")
async def get_market_movers():
    """Return demo market movers."""
    return [
        {"symbol": "NVDA", "change": 5.67},
        {"symbol": "TSLA", "change": -2.34},
        {"symbol": "AAPL", "change": 1.89},
        {"symbol": "GOOGL", "change": 3.21},
        {"symbol": "MSFT", "change": -0.45},
    ]


@router.get("/ai-recommendations")
async def get_ai_recommendations():
    """Return demo AI-powered article recommendations."""
    return [
        {"title": "Tech Stock Analysis Deep Dive", "score": 0.95, "articleId": "1"},
        {"title": "Market Volatility Ahead", "score": 0.87, "articleId": "2"},
        {"title": "Portfolio Rebalancing Tips", "score": 0.73, "articleId": "3"},
    ]
