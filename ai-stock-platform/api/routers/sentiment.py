"""
Sentiment Analysis Router
Created: 2025-06-19 03:09:13
Author: daparthi001
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from core.database import get_db_session
from core.models.response import StandardResponse
from social.twitter_sentiment import TwitterSentimentAnalyzer
from auth.dependencies import get_current_user
from models.user import User
from models.stock import Stock
from models.sentiment import SentimentRecord

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])

# Initialize Twitter sentiment analyzer
twitter_analyzer = TwitterSentimentAnalyzer()

@router.get(
    "/{symbol}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Stock Sentiment Analysis",
    description="Get sentiment analysis for a specific stock symbol based on social media data"
)
async def get_stock_sentiment(
    symbol: str,
    days: int = Query(7, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get sentiment analysis for a stock"""
    try:
        # Get company name for better search results
        stock = await Stock.get_by_symbol(db, symbol)
        company_name = stock.name if stock else None
        
        # Get sentiment analysis
        sentiment_data = await twitter_analyzer.analyze_sentiment(
            symbol=symbol,
            company_name=company_name,
            days=days
        )
        
        return StandardResponse(
            status="success",
            message=f"Successfully retrieved sentiment analysis for {symbol}",
            data=sentiment_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sentiment analysis: {str(e)}"
        )

@router.get(
    "/trending",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Trending Stocks",
    description="Get list of trending stocks based on social media activity"
)
async def get_trending_stocks(
    limit: int = Query(10, description="Number of trending stocks to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get trending stocks based on social media activity"""
    try:
        # Get recent sentiment records
        recent_date = datetime.now() - timedelta(days=1)
        records = await SentimentRecord.get_recent(db, recent_date, limit)
        
        # Format the response
        trending_stocks = []
        
        for record in records:
            # Get stock details
            stock = await Stock.get_by_symbol(db, record.symbol)
            
            trending_stocks.append({
                "symbol": record.symbol,
                "company_name": stock.name if stock else record.symbol