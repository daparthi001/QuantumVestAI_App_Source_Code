import pandas as pd
from typing import Dict, Any, Optional, List
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("api")

class BaseModel:
    """Base class for forecasting models."""
    
    def __init__(self, name: str = "base"):
        """Initialize base model."""
        self.name = name
        self.model = None
        
    def preprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess input data for forecasting.
        
        Args:
            data: DataFrame with historical price data.
                Expected columns: date, open, high, low, close, volume
            
        Returns:
            Preprocessed DataFrame ready for model training/forecasting
        """
        # Ensure data is sorted by date
        data = data.sort_values("date")
        
        # Convert date to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(data.date):
            data["date"] = pd.to_datetime(data.date)
        
        # Fill missing values
        data = data.fillna(method="ffill")
        
        # Feature engineering (to be implemented by child classes)
        return data
    
    def train(self, data: pd.DataFrame) -> bool:
        """
        Train the model on historical data.
        
        Args:
            data: DataFrame with historical price data
            
        Returns:
            True if training was successful, False otherwise
        """
        # Should be implemented by child classes
        logger.warning(f"{self.name} model does not implement train()")
        return False
    
    def forecast(self, data: pd.DataFrame, days: int) -> Optional[Dict[str, Any]]:
        """
        Generate forecast for the specified number of days.
        
        Args:
            data: DataFrame with historical price data
            days: Number of days to forecast
            
        Returns:
            Dictionary with forecast results
        """
        # Should be implemented by child classes
        logger.warning(f"{self.name} model does not implement forecast()")
        return None
    
    def evaluate(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model performance on historical data.
        
        Args:
            data: DataFrame with historical price data
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Should be implemented by child classes
        logger.warning(f"{self.name} model does not implement evaluate()")
        return {
            "rmse": 0.0,
            "mae": 0.0,
            "mape": 0.0,
            "accuracy": 0.0
        }
    
    def _generate_dates(self, start_date: datetime, days: int) -> List[datetime]:
        """
        Generate list of dates for forecast.
        
        Args:
            start_date: First date for forecast
            days: Number of days to generate
            
        Returns:
            List of dates
        """
        dates = []
        current_date = start_date
        
        for _ in range(days):
            # Skip weekends (Saturday = 5, Sunday = 6)
            while current_date.weekday() >= 5:
                current_date += timedelta(days=1)
            
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        return dates
    
    def _calculate_metrics(
        self, actual: np.ndarray, predicted: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate evaluation metrics.
        
        Args:
            actual: Array of actual values
            predicted: Array of predicted values
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((predicted - actual) ** 2))
        
        # Mean Absolute Error
        mae = np.mean(np.abs(predicted - actual))
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        
        # Directional Accuracy
        actual_diff = np.diff(actual)
        predicted_diff = np.diff(predicted)
        directional_accuracy = np.mean(
            (actual_diff > 0) == (predicted_diff > 0)
        ) * 100
        
        return {
            "rmse": round(float(rmse), 2),
            "mae": round(float(mae), 2),
            "mape": round(float(mape), 2),
            "accuracy": round(float(directional_accuracy), 2)
        }
    
    def _format_forecast_response(
        self, 
        ticker: str,
        data: pd.DataFrame,
        forecast_df: pd.DataFrame,
        metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Format forecast results into standardized response.
        
        Args:
            ticker: Stock ticker symbol
            data: Historical data DataFrame
            forecast_df: Forecast data DataFrame
            metrics: Evaluation metrics
            
        Returns:
            Dictionary with formatted forecast results
        """
        # Get current price from the last row of historical data
        current_price = float(data.iloc[-1].close)
        
        # Calculate forecasted prices
        end_price = float(forecast_df.iloc[-1].close)
        peak_price = float(forecast_df.close.max())
        min_price = float(forecast_df.close.min())
        price_range = peak_price - min_price
        
        # Calculate price change percentage
        price_change_pct = (end_price - current_price) / current_price * 100
        
        # Determine trend
        if price_change_pct > 3:
            trend = "Upward"
            trend_strength = "Strong bullish momentum"
        elif price_change_pct > 1:
            trend = "Upward"
            trend_strength = "Moderate bullish momentum"
        elif price_change_pct > -1:
            trend = "Sideways"
            trend_strength = "Neutral momentum"
        elif price_change_pct > -3:
            trend = "Downward"
            trend_strength = "Moderate bearish momentum"
        else:
            trend = "Downward"
            trend_strength = "Strong bearish momentum"
        
        # Determine volatility
        volatility_ratio = price_range / current_price
        if volatility_ratio > 0.1:
            volatility = "High"
            volatility_description = "Significant price fluctuations expected"
        elif volatility_ratio > 0.05:
            volatility = "Medium"
            volatility_description = "Moderate price fluctuations expected"
        else:
            volatility = "Low"
            volatility_description = "Minor price fluctuations expected"
        
        # Determine trading signal
        if price_change_pct > 5 and metrics["accuracy"] > 70:
            signal = "Buy"
            signal_strength = "Strong buy signal"
        elif price_change_pct > 2 and metrics["accuracy"] > 65:
            signal = "Buy"
            signal_strength = "Moderate buy signal"
        elif price_change_pct < -5 and metrics["accuracy"] > 70:
            signal = "Sell"
            signal_strength = "Strong sell signal"
        elif price_change_pct < -2 and metrics["accuracy"] > 65:
            signal = "Sell"
            signal_strength = "Moderate sell signal"
        else:
            signal = "Hold"
            signal_strength = "Neutral signal"
        
        # Create forecast points
        forecast_points = []
        for _, row in forecast_df.iterrows():
            forecast_points.append({
                "date": row.date.strftime("%Y-%m-%d"),
                "price": round(float(row.close), 2),
                "lower": round(float(row.lower_bound), 2) if "lower_bound" in row else None,
                "upper": round(float(row.upper_bound), 2) if "upper_bound" in row else None,
            })
        
        # Generate summary
        summary = (
            f"{ticker} shows a {trend.lower()} trend over the next {len(forecast_points)} days, "
            f"with a predicted price {'increase' if price_change_pct > 0 else 'decrease'} "
            f"of {abs(round(price_change_pct, 2))}%."
        )
        
        # Return complete forecast dict
        return {
            "ticker": ticker,
            "current_price": round(current_price, 2),
            "end_price": round(end_price, 2),
            "peak_price": round(peak_price, 2),
            "minimum_price": round(min_price, 2),
            "price_range": round(price_range, 2),
            "confidence_level": int(metrics["accuracy"]),
            "volatility": volatility,
            "volatility_description": volatility_description,
            "trend": trend,
            "trend_strength": trend_strength,
            "signal": signal,
            "signal_strength": signal_strength,
            "accuracy": round(float(metrics["accuracy"]), 1),
            "forecast_points": forecast_points,
            "metrics": metrics,
            "summary": summary,
            "generated_at": datetime.utcnow().isoformat(),
            "model": self.name
        }