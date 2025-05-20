# Update the function to use the scheduler instead of direct access

from app.main import get_twitter_scheduler

@router.get("/twitter/sentiment/{ticker}")
def get_stock_twitter_sentiment(
    ticker: str,
    days: int = Query(7, ge=1, le=30),
):
    """
    Get Twitter sentiment analysis for a specific stock ticker.
    """
    try:
        scheduler = get_twitter_scheduler()
        if scheduler:
            # Get cached data (and queue refresh if needed)
            return scheduler.get_sentiment(ticker)
        else:
            # Fall back to direct access if scheduler isn't available
            twitter_service = TwitterService()
            return twitter_service.get_sentiment_summary(ticker=ticker, days_back=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Twitter sentiment: {str(e)}")

@router.get("/twitter/trending")
def get_trending_tickers(
    limit: int = Query(10, ge=1, le=50),
):
    """
    Get trending stock tickers on Twitter.
    """
    try:
        scheduler = get_twitter_scheduler()
        if scheduler:
            # Get cached trending data
            trending_data = scheduler.get_trending()
            # Apply limit
            trending_data['trending_tickers'] = trending_data['trending_tickers'][:limit]
            trending_data['count'] = len(trending_data['trending_tickers'])
            return trending_data
        else:
            # Fall back to direct access
            twitter_service = TwitterService()
            trending = twitter_service.get_trending_tickers(limit=limit)
            return {"trending_tickers": trending, "count": len(trending)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trending tickers: {str(e)}")