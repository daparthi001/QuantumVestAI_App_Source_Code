import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from models.arima import ARIMAModel
from models.base import BaseModel
from models.lstm import LSTMModel
from models.prophet import ProphetModel
from models.xgboost_model import XGBoostModel

logger = logging.getLogger("api")

class EnsembleModel(BaseModel):
    """Ensemble model combining predictions from multiple models."""
    
    def __init__(self):
        """Initialize ensemble model with sub-models."""
        super().__init__(name="ensemble")
        
        # Initialize sub-models
        self.models = {
            "lstm": LSTMModel(),
            "prophet": ProphetModel(),
            "xgboost": XGBoostModel(),
            "arima": ARIMAModel()
        }
        
        # Model weights (determined by accuracy on validation data)
        self.weights = {
            "lstm": 0.3,
            "prophet": 0.3,
            "xgboost": 0.25,
            "arima": 0.15
        }
    
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess input data for all sub-models."""
        # Base preprocessing
        processed_data = super().preprocess(data)
        
        # No additional preprocessing needed at ensemble level
        return processed_data
    
    def forecast(self, data: pd.DataFrame, days: int) -> Optional[Dict[str, Any]]:
        """
        Generate ensemble forecast by combining predictions from sub-models.
        
        Args:
            data: DataFrame with historical price data
            days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        try:
            # Preprocess data
            processed_data = self.preprocess(data)
            
            # Get forecasts from each sub-model
            model_forecasts = {}
            valid_models = 0
            
            for model_name, model in self.models.items():
                try:
                    forecast = model.forecast(processed_data, days)
                    if forecast and "forecast_points" in forecast:
                        model_forecasts[model_name] = forecast
                        valid_models += 1
                except Exception as e:
                    logger.warning(f"Error getting forecast from {model_name} model: {e}")
            
            # Require at least 2 valid models for ensemble
            if valid_models < 2:
                logger.error(f"Insufficient valid models for ensemble forecast ({valid_models})")
                
                # Fall back to any single model if available
                for model_name in ["prophet", "lstm", "arima", "xgboost"]:
                    if model_name in model_forecasts:
                        logger.info(f"Falling back to {model_name} model for forecast")
                        return model_forecasts[model_name]
                
                return None
            
            # Create a DataFrame with dates
            last_date = processed_data.date.max()
            forecast_dates = self._generate_dates(last_date + timedelta(days=1), days)
            
            # Prepare ensemble forecast DataFrame
            ensemble_df = pd.DataFrame({
                "date": forecast_dates
            })
            
            # Normalize weights for available models
            weights = {k: v for k, v in self.weights.items() if k in model_forecasts}
            total_weight = sum(weights.values())
            weights = {k: v / total_weight for k, v in weights.items()}
            
            # Combine forecasts with weighted average
            for model_name, forecast in model_forecasts.items():
                model_prices = []
                model_lowers = []
                model_uppers = []
                
                # Extract prices from forecast points
                for point in forecast["forecast_points"]:
                    model_prices.append(point["price"])
                    if "lower" in point and point["lower"] is not None:
                        model_lowers.append(point["lower"])
                    if "upper" in point and point["upper"] is not None:
                        model_uppers.append(point["upper"])
                
                # Add weighted contribution to ensemble
                if len(model_prices) == len(ensemble_df):
                    ensemble_df[f"{model_name}_close"] = model_prices
                    
                    if len(model_lowers) == len(ensemble_df):
                        ensemble_df[f"{model_name}_lower"] = model_lowers
                    
                    if len(model_uppers) == len(ensemble_df):
                        ensemble_df[f"{model_name}_upper"] = model_uppers
            
            # Calculate weighted average prices
            ensemble_df["close"] = 0
            ensemble_df["lower_bound"] = 0
            ensemble_df["upper_bound"] = 0
            
            for model_name, weight in weights.items():
                if f"{model_name}_close" in ensemble_df.columns:
                    ensemble_df["close"] += ensemble_df[f"{model_name}_close"] * weight
                
                if f"{model_name}_lower" in ensemble_df.columns:
                    ensemble_df["lower_bound"] += ensemble_df[f"{model_name}_lower"] * weight
                else:
                    ensemble_df["lower_bound"] += ensemble_df[f"{model_name}_close"] * weight * 0.95
                
                if f"{model_name}_upper" in ensemble_df.columns:
                    ensemble_df["upper_bound"] += ensemble_df[f"{model_name}_upper"] * weight
                else:
                    ensemble_df["upper_bound"] += ensemble_df[f"{model_name}_close"] * weight * 1.05
            
            # Calculate average metrics
            avg_metrics = {
                "rmse": 0,
                "mae": 0,
                "mape": 0,
                "accuracy": 0
            }
            
            for model_name, forecast in model_forecasts.items():
                for metric, value in forecast.get("metrics", {}).items():
                    if metric in avg_metrics:
                        avg_metrics[metric] += value * weights.get(model_name, 0)
            
            # Format and return ensemble forecast
            return self._format_forecast_response(
                ticker=data.iloc[0].ticker if "ticker" in data.columns else "UNKNOWN",
                data=processed_data,
                forecast_df=ensemble_df,
                metrics=avg_metrics
            )
            
        except Exception as e:
            logger.exception(f"Error in ensemble forecast: {e}")
            return None
    
    def evaluate(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate ensemble model on historical data.
        
        Args:
            data: DataFrame with historical price data
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Get metrics from each sub-model
        model_metrics = {}
        valid_models = 0
        
        for model_name, model in self.models.items():
            try:
                metrics = model.evaluate(data)
                if metrics:
                    model_metrics[model_name] = metrics
                    valid_models += 1
            except Exception as e:
                logger.warning(f"Error evaluating {model_name} model: {e}")
        
        # Calculate weighted average metrics
        if valid_models == 0:
            return super().evaluate(data)
        
        # Normalize weights for available models
        weights = {k: v for k, v in self.weights.items() if k in model_metrics}
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}
        
        # Calculate weighted average metrics
        avg_metrics = {
            "rmse": 0,
            "mae": 0,
            "mape": 0,
            "accuracy": 0
        }
        
        for model_name, metrics in model_metrics.items():
            for metric, value in metrics.items():
                if metric in avg_metrics:
                    avg_metrics[metric] += value * weights.get(model_name, 0)
        
        # Round metrics
        for metric in avg_metrics:
            avg_metrics[metric] = round(avg_metrics[metric], 2)
        
        return avg_metrics
