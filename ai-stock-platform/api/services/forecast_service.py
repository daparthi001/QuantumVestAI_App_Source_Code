from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from api.db.models.stock import Stock, StockPrice
from api.models.ensemble import EnsembleModel
from api.models.lstm import LSTMModel
from api.models.prophet import ProphetModel
from api.models.xgboost_model import XGBoostModel
from api.models.arima import ARIMAModel

class ForecastService:
    """Service for generating stock forecasts."""
    
    def __init__(self, db: Session):
        self.db = db
        self.models = {
            "ensemble": EnsembleModel(),
            "lstm": LSTMModel(),
            "prophet": ProphetModel(),
            "xgboost": XGBoostModel(),
            "arima": ARIMAModel()
        }
    
    def get_forecast(self, ticker: str, days: int, model_name: str) -> Optional[Dict[str, Any]]:
        """Generate a forecast for the specified stock and model."""
        # Get stock from database
        stock = self.db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            return None
        
        # Get historical price data
        prices = self.db.query(StockPrice).filter(
            StockPrice.stock_id == stock.id
        ).order_by(StockPrice.date.desc()).limit(365).all()
        
        if not prices:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                "date": price.date,
                "open": price.open,
                "high": price.high,
                "low": price.low,
                "close": price.close,
                "volume": price.volume
            }
            for price in prices
        ])
        
        # Sort by date
        df = df.sort_values("date")
        
        # Get model
        model = self.models.get(model_name)
        if not model:
            return None
        
        # Generate forecast
        forecast = model.forecast(df, days)
        if not forecast:
            return None
        
        # Add metadata
        forecast["ticker"] = ticker
        forecast["model"] = model_name
        forecast["generated_at"] = datetime.utcnow().isoformat()
        
        return forecast
    
    def compare_models(self, ticker: str, days: int) -> Dict[str, Dict[str, float]]:
        """Compare different forecast models for a stock."""
        result = {}
        
        # Get forecasts for each model
        for model_name in self.models.keys():
            forecast = self.get_forecast(ticker, days, model_name)
            if forecast:
                # Extract metrics
                result[model_name] = {
                    "rmse": forecast.get("metrics", {}).get("rmse", 0.0),
                    "mae": forecast.get("metrics", {}).get("mae", 0.0),
                    "mape": forecast.get("metrics", {}).get("mape", 0.0),
                    "accuracy": forecast.get("metrics", {}).get("accuracy", 0.0)
                }
        
        return result
    
    def get_predictability(self, ticker: str) -> Dict[str, Any]:
        """Calculate predictability metrics for a stock."""
        # Get stock from database
        stock = self.db.query(Stock).filter(Stock.ticker == ticker).first()
        if not stock:
            return {
                "score": 0,
                "category": "Unknown",
                "factors": {}
            }
        
        # Use stored predictability metrics if available
        if stock.predictability_score:
            factors = {
                "volatility": {
                    "score": stock.volatility_score or 0,
                    "description": self._get_volatility_description(stock.volatility_score or 0)
                },
                "trend": {
                    "score": stock.trend_score or 0,
                    "description": self._get_trend_description(stock.trend_score or 0)
                },
                "volume": {
                    "score": stock.volume_score or 0,
                    "description": self._get_volume_description(stock.volume_score or 0)
                }
            }
            
            return {
                "score": stock.predictability_score,
                "category": self._get_predictability_category(stock.predictability_score),
                "factors": factors
            }
        
        # Calculate predictability metrics
        # (In a real implementation, this would be more sophisticated)
        volatility_score = np.random.randint(60, 95)
        trend_score = np.random.randint(60, 95)
        volume_score = np.random.randint(60, 95)
        
        # Calculate overall score as weighted average
        overall_score = int(0.4 * volatility_score + 0.4 * trend_score + 0.2 * volume_score)
        
        # Store scores in database
        stock.predictability_score = overall_score
        stock.volatility_score = volatility_score
        stock.trend_score = trend_score
        stock.volume_score = volume_score
        self.db.commit()
        
        factors = {
            "volatility": {
                "score": volatility_score,
                "description": self._get_volatility_description(volatility_score)
            },
            "trend": {
                "score": trend_score,
                "description": self._get_trend_description(trend_score)
            },
            "volume": {
                "score": volume_score,
                "description": self._get_volume_description(volume_score)
            }
        }
        
        return {
            "score": overall_score,
            "category": self._get_predictability_category(overall_score),
            "factors": factors
        }
    
    def backtest(
        self, 
        ticker: str, 
        days: int, 
        start_date: str, 
        end_date: str, 
        model_name: str
    ) -> Dict[str, Any]:
        """Backtest a forecast model on historical data."""
        # In a real implementation, this would run actual backtests
        # For this example, we'll return mock data
        
        return {
            "ticker": ticker,
            "model": model_name,
            "days": days,
            "start_date": start_date,
            "end_date": end_date,
            "summary": {
                "accuracy": 87.5,
                "profit_loss": 8.7,
                "win_rate": 72,
                "trades": 18
            },
            "metrics": {
                "rmse": 1.47,
                "mae": 1.21,
                "mape": 0.65
            },
            "trades": [
                {
                    "date": "2025-04-15",
                    "action": "buy",
                    "price": 150.25,
                    "predicted": 158.10,
                    "actual": 157.35,
                    "result": 4.7
                },
                {
                    "date": "2025-04-08",
                    "action": "buy",
                    "price": 148.75,
                    "predicted": 155.20,
                    "actual": 153.95,
                    "result": 3.5
                }
            ]
        }
    
    def _get_predictability_category(self, score: int) -> str:
        """Convert predictability score to category."""
        if score >= 85:
            return "Very High"
        elif score >= 70:
            return "High"
        elif score >= 50:
            return "Medium"
        elif score >= 30:
            return "Low"
        else:
            return "Very Low"
    
    def _get_volatility_description(self, score: int) -> str:
        """Generate description for volatility score."""
        if score >= 85:
            return "Very stable price movements making forecasting more reliable"
        elif score >= 70:
            return "Moderate volatility creates manageable price patterns"
        elif score >= 50:
            return "Average volatility with some predictable patterns"
        elif score >= 30:
            return "High volatility makes price movements less predictable"
        else:
            return "Extreme volatility makes forecasting very challenging"
    
    def _get_trend_description(self, score: int) -> str:
        """Generate description for trend score."""
        if score >= 85:
            return "Strong and consistent directional trend"
        elif score >= 70:
            return "Clear trend with occasional reversals"
        elif score >= 50:
            return "Moderate trending behavior"
        elif score >= 30:
            return "Weak trends with frequent direction changes"
        else:
            return "No discernible trend pattern"
    
    def _get_volume_description(self, score: int) -> str:
        """Generate description for volume score."""
        if score >= 85:
            return "High and consistent trading volume creates reliable signals"
        elif score >= 70:
            return "Good trading volume with clear patterns"
        elif score >= 50:
            return "Adequate volume for most forecasting methods"
        elif score >= 30:
            return "Low volume may reduce forecast reliability"
        else:
            return "Very thin trading makes forecasting difficult"