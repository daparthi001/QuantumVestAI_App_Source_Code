"""
Enhanced Sentiment Analysis API Routes
Created: 2025-01-09
Author: AI Assistant for QuantumVestAI
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from api.social.multi_source_sentiment import MultiSourceSentimentAnalyzer
from api.services.notification_manager import notification_manager, NotificationChannel, NotificationPriority
from api.services.premium_manager import premium_manager
from core.auth import get_current_user
from schemas.sentiment import SentimentAnalysisRequest, SentimentAnalysisResponse

logger = logging.getLogger("api.routes.sentiment")

router = APIRouter(prefix="/api/v1/sentiment", tags=["sentiment"])

@router.get("/stocks/{symbol}")
async def get_stock_sentiment(
    symbol: str,
    days: int = 7,
    sources: Optional[str] = None,
    user = Depends(get_current_user)
):
    """Get comprehensive sentiment analysis for a stock"""
    
    # Check user permissions
    user_tier = premium_manager.get_user_tier(user.id)
    usage_check = premium_manager.check_usage_limit(
        user.id, 
        "sentiment_analysis", 
        "sentiment_queries"
    )
    
    if not usage_check["allowed"]:
        raise HTTPException(
            status_code=403,
            detail=f"Sentiment analysis limit reached. {usage_check['reason']}"
        )
    
    try:
        # Initialize multi-source analyzer
        async with MultiSourceSentimentAnalyzer() as analyzer:
            # Get company name for better analysis
            company_name = await get_company_name(symbol)
            
            # Perform comprehensive sentiment analysis
            sentiment_data = await analyzer.analyze_comprehensive_sentiment(
                symbol=symbol,
                company_name=company_name,
                days=days
            )
            
            # Increment usage
            premium_manager.increment_usage(user.id, "sentiment_queries")
            
            # Prepare response based on user tier
            response_data = prepare_sentiment_response(sentiment_data, user_tier)
            
            return JSONResponse(content={
                "success": True,
                "data": response_data,
                "metadata": {
                    "symbol": symbol,
                    "analysis_period_days": days,
                    "user_tier": user_tier.value,
                    "remaining_queries": usage_check["remaining"]
                }
            })
            
    except Exception as e:
        logger.error(f"Sentiment analysis failed for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze sentiment. Please try again later."
        )

@router.get("/stocks/{symbol}/real-time")
async def get_real_time_sentiment(
    symbol: str,
    user = Depends(get_current_user)
):
    """Get real-time sentiment updates for a stock"""
    
    # Premium feature check
    if not premium_manager.has_feature_access(user.id, "premium_alerts"):
        raise HTTPException(
            status_code=403,
            detail="Real-time sentiment requires Premium subscription"
        )
    
    try:
        async with MultiSourceSentimentAnalyzer() as analyzer:
            # Get recent sentiment (last hour)
            sentiment_data = await analyzer.analyze_comprehensive_sentiment(
                symbol=symbol,
                days=1  # Last 24 hours but focus on recent data
            )
            
            # Add real-time indicators
            sentiment_data["real_time"] = True
            sentiment_data["update_frequency"] = "5 minutes"
            sentiment_data["last_update"] = datetime.now().isoformat()
            
            return JSONResponse(content={
                "success": True,
                "data": sentiment_data
            })
            
    except Exception as e:
        logger.error(f"Real-time sentiment failed for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get real-time sentiment"
        )

@router.get("/market/overview")
async def get_market_sentiment_overview(
    sectors: Optional[str] = None,
    user = Depends(get_current_user)
):
    """Get overall market sentiment overview"""
    
    try:
        # Analyze sentiment for major market indices and sectors
        major_symbols = ["SPY", "QQQ", "IWM", "DIA"]
        if sectors:
            sector_symbols = sectors.split(",")
            major_symbols.extend(sector_symbols)
        
        sentiment_tasks = []
        async with MultiSourceSentimentAnalyzer() as analyzer:
            for symbol in major_symbols:
                task = analyzer.analyze_comprehensive_sentiment(symbol, days=3)
                sentiment_tasks.append((symbol, task))
            
            # Execute all analysis tasks concurrently
            results = {}
            for symbol, task in sentiment_tasks:
                try:
                    sentiment_data = await task
                    results[symbol] = {
                        "overall_sentiment": sentiment_data["overall_sentiment"],
                        "confidence": sentiment_data["confidence"],
                        "sentiment_category": sentiment_data["sentiment_category"],
                        "market_impact": sentiment_data["market_impact"]
                    }
                except Exception as e:
                    logger.error(f"Failed to analyze {symbol}: {e}")
                    results[symbol] = {"error": "Analysis failed"}
            
            # Calculate overall market sentiment
            valid_sentiments = [
                data["overall_sentiment"] for data in results.values() 
                if "overall_sentiment" in data
            ]
            
            if valid_sentiments:
                market_sentiment = sum(valid_sentiments) / len(valid_sentiments)
                market_category = categorize_sentiment(market_sentiment)
            else:
                market_sentiment = 0.0
                market_category = "Neutral"
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "market_sentiment": round(market_sentiment, 4),
                    "market_category": market_category,
                    "individual_symbols": results,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "symbols_analyzed": len(major_symbols),
                    "successful_analysis": len(valid_sentiments)
                }
            })
            
    except Exception as e:
        logger.error(f"Market sentiment overview failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get market sentiment overview"
        )

@router.post("/alerts/create")
async def create_sentiment_alert(
    symbol: str,
    threshold: float,
    condition: str,  # "above" or "below"
    channels: List[str],
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """Create a sentiment-based alert"""
    
    # Check premium access
    if not premium_manager.has_feature_access(user.id, "premium_alerts"):
        raise HTTPException(
            status_code=403,
            detail="Sentiment alerts require Premium subscription"
        )
    
    # Validate inputs
    if condition not in ["above", "below"]:
        raise HTTPException(
            status_code=400,
            detail="Condition must be 'above' or 'below'"
        )
    
    if not -1.0 <= threshold <= 1.0:
        raise HTTPException(
            status_code=400,
            detail="Threshold must be between -1.0 and 1.0"
        )
    
    valid_channels = ["email", "push", "sms"]
    notification_channels = []
    for channel in channels:
        if channel in valid_channels:
            notification_channels.append(NotificationChannel(channel.upper()))
    
    if not notification_channels:
        raise HTTPException(
            status_code=400,
            detail="At least one valid notification channel required"
        )
    
    try:
        # Store alert in database (simulated here)
        alert_id = f"sentiment_alert_{user.id}_{symbol}_{datetime.now().timestamp()}"
        
        # Schedule background monitoring
        background_tasks.add_task(
            monitor_sentiment_alert,
            alert_id,
            user.id,
            symbol,
            threshold,
            condition,
            notification_channels
        )
        
        # Send confirmation
        await notification_manager.send_notification({
            "user_id": user.id,
            "title": "Sentiment Alert Created",
            "message": f"Alert for {symbol} when sentiment goes {condition} {threshold}",
            "channels": [NotificationChannel.EMAIL],
            "priority": NotificationPriority.NORMAL
        })
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "alert_id": alert_id,
                "symbol": symbol,
                "threshold": threshold,
                "condition": condition,
                "channels": channels,
                "status": "active"
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to create sentiment alert: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create sentiment alert"
        )

@router.get("/trending/topics")
async def get_trending_sentiment_topics(
    limit: int = 10,
    timeframe: str = "24h",
    user = Depends(get_current_user)
):
    """Get trending sentiment topics and discussions"""
    
    try:
        # Simulate trending topics analysis
        # In real implementation, this would analyze social media trends
        trending_topics = [
            {
                "topic": "AI Trading Strategies",
                "sentiment": 0.65,
                "category": "Very Positive",
                "volume": 2847,
                "growth": "+127%",
                "related_stocks": ["NVDA", "GOOGL", "MSFT"]
            },
            {
                "topic": "Federal Reserve Policy",
                "sentiment": -0.23,
                "category": "Negative",
                "volume": 1923,
                "growth": "+89%",
                "related_stocks": ["SPY", "TLT", "USD"]
            },
            {
                "topic": "Electric Vehicle Market",
                "sentiment": 0.41,
                "category": "Positive",
                "volume": 1654,
                "growth": "+45%",
                "related_stocks": ["TSLA", "RIVN", "LCID"]
            },
            {
                "topic": "Cryptocurrency Integration",
                "sentiment": 0.12,
                "category": "Neutral",
                "volume": 1234,
                "growth": "+23%",
                "related_stocks": ["COIN", "MSTR", "SQ"]
            },
            {
                "topic": "Healthcare Innovation",
                "sentiment": 0.78,
                "category": "Very Positive",
                "volume": 987,
                "growth": "+67%",
                "related_stocks": ["JNJ", "PFE", "MRNA"]
            }
        ]
        
        # Limit results
        trending_topics = trending_topics[:limit]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "trending_topics": trending_topics,
                "timeframe": timeframe,
                "total_topics": len(trending_topics),
                "analysis_timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get trending topics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get trending sentiment topics"
        )

@router.get("/compare")
async def compare_stock_sentiments(
    symbols: str,  # Comma-separated list
    days: int = 7,
    user = Depends(get_current_user)
):
    """Compare sentiment across multiple stocks"""
    
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    if len(symbol_list) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 stocks can be compared at once"
        )
    
    # Check usage limits
    usage_check = premium_manager.check_usage_limit(
        user.id, 
        "sentiment_analysis", 
        "sentiment_queries"
    )
    
    queries_needed = len(symbol_list)
    if usage_check["remaining"] < queries_needed:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient queries remaining. Need {queries_needed}, have {usage_check['remaining']}"
        )
    
    try:
        comparison_results = {}
        
        async with MultiSourceSentimentAnalyzer() as analyzer:
            # Analyze each stock
            for symbol in symbol_list:
                try:
                    sentiment_data = await analyzer.analyze_comprehensive_sentiment(
                        symbol=symbol,
                        days=days
                    )
                    
                    comparison_results[symbol] = {
                        "overall_sentiment": sentiment_data["overall_sentiment"],
                        "confidence": sentiment_data["confidence"],
                        "sentiment_category": sentiment_data["sentiment_category"],
                        "market_impact": sentiment_data["market_impact"],
                        "total_volume": sentiment_data["total_volume"],
                        "sources": len(sentiment_data["sources"])
                    }
                    
                    # Increment usage
                    premium_manager.increment_usage(user.id, "sentiment_queries")
                    
                except Exception as e:
                    logger.error(f"Failed to analyze {symbol}: {e}")
                    comparison_results[symbol] = {"error": "Analysis failed"}
            
            # Generate comparison insights
            valid_results = {k: v for k, v in comparison_results.items() if "error" not in v}
            
            insights = []
            if len(valid_results) >= 2:
                # Find most/least positive
                most_positive = max(valid_results.items(), key=lambda x: x[1]["overall_sentiment"])
                least_positive = min(valid_results.items(), key=lambda x: x[1]["overall_sentiment"])
                
                insights.append(f"Most positive sentiment: {most_positive[0]} ({most_positive[1]['sentiment_category']})")
                insights.append(f"Least positive sentiment: {least_positive[0]} ({least_positive[1]['sentiment_category']})")
                
                # Find highest confidence
                highest_confidence = max(valid_results.items(), key=lambda x: x[1]["confidence"])
                insights.append(f"Highest confidence analysis: {highest_confidence[0]} ({highest_confidence[1]['confidence']:.1%})")
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "comparison": comparison_results,
                    "insights": insights,
                    "symbols_analyzed": len(symbol_list),
                    "successful_analysis": len(valid_results),
                    "analysis_period_days": days,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            })
            
    except Exception as e:
        logger.error(f"Sentiment comparison failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to compare stock sentiments"
        )

# Helper functions

async def get_company_name(symbol: str) -> Optional[str]:
    """Get company name for symbol"""
    # In real implementation, this would query a stock database
    company_names = {
        "AAPL": "Apple Inc.",
        "GOOGL": "Alphabet Inc.",
        "MSFT": "Microsoft Corporation",
        "AMZN": "Amazon.com Inc.",
        "TSLA": "Tesla Inc.",
        "NVDA": "NVIDIA Corporation",
        "META": "Meta Platforms Inc.",
        "SPY": "SPDR S&P 500 ETF Trust",
        "QQQ": "Invesco QQQ Trust"
    }
    return company_names.get(symbol.upper())

def prepare_sentiment_response(sentiment_data: Dict[str, Any], user_tier) -> Dict[str, Any]:
    """Prepare sentiment response based on user tier"""
    response = {
        "overall_sentiment": sentiment_data["overall_sentiment"],
        "confidence": sentiment_data["confidence"],
        "sentiment_category": sentiment_data["sentiment_category"],
        "market_impact": sentiment_data["market_impact"],
        "analysis_timestamp": sentiment_data["analysis_timestamp"]
    }
    
    # Add more details for premium users
    if user_tier.value in ["premium", "enterprise"]:
        response.update({
            "sources": sentiment_data["sources"],
            "total_volume": sentiment_data["total_volume"]
        })
    
    # Add even more details for enterprise users
    if user_tier.value == "enterprise":
        response.update({
            "raw_data": sentiment_data.get("raw_data", {}),
            "confidence_breakdown": sentiment_data.get("confidence_breakdown", {}),
            "historical_comparison": sentiment_data.get("historical_comparison", {})
        })
    
    return response

def categorize_sentiment(sentiment: float) -> str:
    """Categorize sentiment score"""
    if sentiment > 0.3:
        return "Very Positive"
    elif sentiment > 0.1:
        return "Positive"
    elif sentiment > -0.1:
        return "Neutral"
    elif sentiment > -0.3:
        return "Negative"
    else:
        return "Very Negative"

async def monitor_sentiment_alert(
    alert_id: str,
    user_id: str,
    symbol: str,
    threshold: float,
    condition: str,
    channels: List[NotificationChannel]
):
    """Background task to monitor sentiment alerts"""
    
    try:
        while True:
            async with MultiSourceSentimentAnalyzer() as analyzer:
                sentiment_data = await analyzer.analyze_comprehensive_sentiment(
                    symbol=symbol,
                    days=1
                )
                
                current_sentiment = sentiment_data["overall_sentiment"]
                
                # Check if alert should trigger
                should_trigger = False
                if condition == "above" and current_sentiment > threshold:
                    should_trigger = True
                elif condition == "below" and current_sentiment < threshold:
                    should_trigger = True
                
                if should_trigger:
                    # Send alert
                    await notification_manager.send_sentiment_alert(
                        user_id=user_id,
                        symbol=symbol,
                        sentiment_score=current_sentiment,
                        sentiment_category=sentiment_data["sentiment_category"],
                        channels=channels
                    )
                    
                    # Alert triggered, stop monitoring
                    break
                
                # Wait before next check (5 minutes for demo)
                await asyncio.sleep(300)
                
    except Exception as e:
        logger.error(f"Sentiment alert monitoring failed for {alert_id}: {e}")

# Include router in main app
def include_sentiment_routes(app):
    app.include_router(router)