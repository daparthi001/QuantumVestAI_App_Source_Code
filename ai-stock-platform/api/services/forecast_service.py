"""Simple forecast service using built-in models."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd

from services.stock_service import StockService
from ml.ensemble_model import (
    EnsemblePredictor,
    linear_regression_predict,
    random_forest_predict,
)

class ForecastService:
    """Provide basic forecast functionality for demo purposes."""

    def __init__(self, db):
        self.db = db

    async def _get_history(self, ticker: str, days: int = 120) -> Optional[pd.DataFrame]:
        stock_service = StockService(self.db)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        data = await stock_service.get_historical_prices(
            symbol=ticker,
            start_date=start_date,
            end_date=end_date
        )
        if not data:
            return None
        df = pd.DataFrame(data)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        return df

    async def get_forecast(
        self,
        ticker: str,
        days: int = 7,
        model: str = "ensemble",
        include_sentiment: bool = False
    ) -> Optional[Dict[str, Any]]:
        history = await self._get_history(ticker)
        if history is None or 'adjusted_close' not in history.columns:
            return None

        predictor = EnsemblePredictor()
        predictor.add_model(linear_regression_predict)
        predictor.add_model(random_forest_predict)
        preds = predictor.predict(ticker, history[['adjusted_close']], days_ahead=days)

        current = float(history['adjusted_close'].iloc[-1])
        forecast_price = float(preds['predicted_close'].iloc[-1])
        change_pct = (forecast_price - current) / current * 100

        return {
            "symbol": ticker,
            "model": model,
            "horizon": days,
            "forecast": [
                {
                    "date": d.isoformat(),
                    "predicted_price": float(p),
                    "confidence_upper": float(p * 1.05),
                    "confidence_lower": float(p * 0.95),
                    "confidence_level": 0.8,
                }
                for d, p in zip(preds.index, preds['predicted_close'])
            ],
            "model_metrics": {
                "accuracy": 0.75,
                "mae": 2.0,
                "rmse": 2.5,
                "last_trained": datetime.utcnow().isoformat()
            },
            "current_price": current,
            "forecast_price": forecast_price,
            "change_percent": change_pct,
            "confidence": 80.0,
            "signal": "Buy" if change_pct > 0 else "Sell"
        }

    async def compare_models(self, ticker: str, days: int) -> Dict[str, Any]:
        models = ["ensemble", "lstm", "prophet"]
        results = []
        for m in models:
            forecast = await self.get_forecast(ticker, days, model=m)
            if forecast:
                results.append({"model": m, "accuracy": 0.75})
        return {"models": results}

    async def get_predictability(self, ticker: str) -> Dict[str, Any]:
        return {"ticker": ticker, "score": 70}

    async def backtest(self, ticker: str, days: int, start_date: str, end_date: str, model: str) -> Dict[str, Any]:
        return {"ticker": ticker, "model": model, "days": days, "return": 5.0}

    async def get_recommendations(self, limit: int, user_id: str) -> Dict[str, Any]:
        return {"recommendations": ["AAPL", "MSFT"][:limit]}
