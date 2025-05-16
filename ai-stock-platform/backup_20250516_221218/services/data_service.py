import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import Depends

from api.db.models.stock import Stock, StockPrice
from api.utils.pipeline import (
    DataPipeline, DataFetchStage, DataCleanStage, 
    FeatureEngineeringStage, PredictabilityAnalysisStage
)
from api.models.finbert_sentiment import FinBertSentiment
from api.core.cache import cache

logger = logging.getLogger("api")

class DataService:
    """Service for fetching and processing stock data."""
    
    def __init__(self, db: Session):
        """
        Initialize data service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.pipeline = self._create_pipeline()
        self.finbert = FinBertSentiment()
    
    def _create_pipeline(self) -> DataPipeline:
        """
        Create data processing pipeline.
        
        Returns:
            Configured pipeline instance
        """
        pipeline = DataPipeline()
        
        # Add pipeline stages
        pipeline.add_stage(DataFetchStage())
        pipeline.add_stage(DataCleanStage())
        pipeline.add_stage(FeatureEngineeringStage())
        pipeline.add_stage(PredictabilityAnalysisStage())
        
        return pipeline
    
    @cache(ttl_seconds=3600, key_prefix="stock_data")
    async def get_stock_data(
        self, ticker: str, period: str = "1y", include_sentiment: bool = False
    ) -> Dict[str, Any]:
        """
        Get processed stock data for forecasting.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (e.g., "1y", "6mo", etc.)
            include_sentiment: Whether to include sentiment analysis
            
        Returns:
            Dictionary with processed stock data
        """
        try:
            # Execute pipeline
            pipeline_data = await self.pipeline.execute(
                ticker=ticker,
                period=period,
                include_sentiment=include_sentiment
            )
            
            # Store latest data in database if available
            if pipeline_data.get("processed_data") is not None:
                self._update_stock_data(pipeline_data)
            
            return {
                "ticker": ticker,
                "period": period,
                "data": pipeline_data.get("processed_data"),
                "features": pipeline_data.get("features", {}),
                "predictability": pipeline_data.get("predictability"),
                "sentiment": pipeline_data.get("sentiment"),
                "metadata": pipeline_data.get("metadata", {}),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.exception(f"Error getting stock data for {ticker}: {e}")
            return {
                "ticker": ticker,
                "error": str(e),
                "metadata": {
                    "success": False,
                    "error_type": e.__class__.__name__
                }
            }
    
    @cache(ttl_seconds=86400, key_prefix="sentiment_analysis")
    async def get_sentiment_analysis(self, ticker: str) -> Dict[str, Any]:
        """
        Get sentiment analysis for a stock ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            pipeline_data = await self.pipeline.execute(
                ticker=ticker,
                period="3mo",
                include_sentiment=True
            )
            
            sentiment = pipeline_data.get("sentiment")
            if sentiment is None:
                return {
                    "ticker": ticker,
                    "error": "No sentiment data available",
                    "success": False
                }
            
            return {
                "ticker": ticker,
                "sentiment": sentiment,
                "generated_at": datetime.utcnow().isoformat(),
                "success": True
            }
        except Exception as e:
            logger.exception(f"Error getting sentiment analysis for {ticker}: {e}")
            return {
                "ticker": ticker,
                "error": str(e),
                "success": False
            }
    
    @cache(ttl_seconds=86400, key_prefix="predictability_analysis")
    async def get_predictability_analysis(self, ticker: str) -> Dict[str, Any]:
        """
        Get predictability analysis for a stock ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with predictability analysis results
        """
        try:
            pipeline_data = await self.pipeline.execute(
                ticker=ticker,
                period="6mo",
                include_sentiment=False
            )
            
            predictability = pipeline_data.get("predictability")
            if predictability is None:
                return {
                    "ticker": ticker,
                    "error": "Could not perform predictability analysis",
                    "success": False
                }
            
            return {
                "ticker": ticker,
                "predictability": predictability,
                "generated_at": datetime.utcnow().isoformat(),
                "success": True
            }
        except Exception as e:
            logger.exception(f"Error getting predictability analysis for {ticker}: {e}")
            return {
                "ticker": ticker,
                "error": str(e),
                "success": False
            }
    
    def _update_stock_data(self, pipeline_data: Dict[str, Any]) -> None:
        """
        Update stock data in database.
        
        Args:
            pipeline_data: Data from pipeline execution
        """
        try:
            df = pipeline_data.get("processed_data")
            if df is None or df.empty:
                return
            
            ticker = pipeline_data.get("ticker", "")
            if not ticker:
                return
            
            # Get or create stock record
            stock = self.db.query(Stock).filter(Stock.ticker == ticker).first()
            if not stock:
                # Get the latest price
                latest = df.iloc[-1]
                
                stock = Stock(
                    ticker=ticker,
                    name=ticker,  # In a real implementation, get actual name
                    exchange="NYSE",  # In a real implementation, get actual exchange
                    last_price=float(latest.close) if "close" in latest else None,
                    last_updated=latest.date if "date" in latest else datetime.utcnow()
                )
                
                # Add predictability metrics if available
                if "predictability" in pipeline_data:
                    pred = pipeline_data["predictability"]
                    stock.predictability_score = pred.get("score")
                    stock.volatility_score = pred.get("factors", {}).get("volatility", {}).get("score")
                    stock.trend_score = pred.get("factors", {}).get("trend", {}).get("score")
                    stock.volume_score = pred.get("factors", {}).get("volume", {}).get("score")
                
                self.db.add(stock)
                self.db.commit()
                self.db.refresh(stock)
            else:
                # Update last price and predictability metrics
                latest = df.iloc[-1]
                stock.last_price = float(latest.close) if "close" in latest else stock.last_price
                stock.last_updated = latest.date if "date" in latest else datetime.utcnow()
                
                # Update predictability metrics if available
                if "predictability" in pipeline_data:
                    pred = pipeline_data["predictability"]
                    stock.predictability_score = pred.get("score")
                    stock.volatility_score = pred.get("factors", {}).get("volatility", {}).get("score")
                    stock.trend_score = pred.get("factors", {}).get("trend", {}).get("score")
                    stock.volume_score = pred.get("factors", {}).get("volume", {}).get("score")
                
                self.db.commit()
                
            # In a real implementation, also update historical price records in StockPrice table
            # This is omitted here for brevity
            
        except Exception as e:
            logger.exception(f"Error updating stock data: {e}")
            # Rollback transaction
            self.db.rollback()