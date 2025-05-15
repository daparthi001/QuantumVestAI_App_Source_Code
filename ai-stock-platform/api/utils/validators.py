"""
Utility functions for input validation.

These functions handle validation of user inputs and data structures
to ensure data integrity and security.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import re
from datetime import datetime, timedelta

logger = logging.getLogger("api")

def validate_ticker(ticker: str) -> bool:
    """
    Validate a stock ticker symbol.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check if ticker is empty
        if not ticker:
            return False
        
        # Basic validation: alphanumeric with some special characters
        pattern = r'^[A-Za-z0-9\.\-\^]{1,10}$'
        return bool(re.match(pattern, ticker))
    
    except Exception as e:
        logger.exception(f"Error validating ticker: {e}")
        return False

def validate_date_range(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    max_days: int = 3650  # Default 10 years
) -> Tuple[bool, Optional[str]]:
    """
    Validate a date range for stock data.
    
    Args:
        start_date: Start date in format YYYY-MM-DD
        end_date: End date in format YYYY-MM-DD
        max_days: Maximum allowed days in range
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # If both dates are None, it's valid (can use defaults)
        if start_date is None and end_date is None:
            return True, None
        
        # Date format validation
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        
        if start_date and not re.match(date_pattern, start_date):
            return False, f"Invalid start_date format: {start_date}. Use YYYY-MM-DD."
        
        if end_date and not re.match(date_pattern, end_date):
            return False, f"Invalid end_date format: {end_date}. Use YYYY-MM-DD."
        
        # Parse dates
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=365)
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        except ValueError as e:
            return False, f"Date parsing error: {e}"
        
        # End date must be after start date
        if end_dt < start_dt:
            return False, f"End date ({end_date}) must be after start date ({start_date})"
        
        # Check range is not too large
        days_diff = (end_dt - start_dt).days
        if days_diff > max_days:
            return False, f"Date range too large: {days_diff} days (max: {max_days})"
        
        # Check that dates are not in the future
        now = datetime.now()
        if end_dt > now:
            return False, f"End date ({end_date}) cannot be in the future"
        
        return True, None
        
    except Exception as e:
        logger.exception(f"Error validating date range: {e}")
        return False, f"Validation error: {str(e)}"

def validate_forecast_params(
    ticker: str, 
    days: int, 
    model: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate parameters for stock forecast.
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days to forecast
        model: Forecasting model name
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Validate ticker
        if not validate_ticker(ticker):
            return False, f"Invalid ticker symbol: {ticker}"
        
        # Validate days
        if days < 1:
            return False, "Forecast days must be at least 1"
        if days > 90:
            return False, f"Forecast days too large: {days} (max: 90)"
        
        # Validate model
        valid_models = ["ensemble", "lstm", "prophet", "xgboost", "arima"]
        if model not in valid_models:
            return False, f"Invalid model: {model}. Valid models: {', '.join(valid_models)}"
        
        return True, None
        
    except Exception as e:
        logger.exception(f"Error validating forecast parameters: {e}")
        return False, f"Validation error: {str(e)}"

def validate_model_params(
    model_params: Dict[str, Any],
    model_type: str
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate model hyperparameters.
    
    Args:
        model_params: Dictionary of model parameters
        model_type: Type of model
        
    Returns:
        Tuple of (is_valid, error_message, sanitized_params)
    """
    try:
        # Make a copy to avoid modifying the original
        params = model_params.copy() if model_params else {}
        
        # Default parameters for each model type
        defaults = {
            "lstm": {
                "lookback_days": 30,
                "epochs": 50,
                "batch_size": 32,
                "hidden_units": 64,
                "dropout": 0.2,
                "learning_rate": 0.001
            },
            "prophet": {
                "changepoint_prior_scale": 0.05,
                "seasonality_prior_scale": 10.0,
                "seasonality_mode": "multiplicative",
                "yearly_seasonality": True,
                "weekly_seasonality": True,
                "daily_seasonality": False
            },
            "xgboost": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "objective": "reg:squarederror"
            },
            "arima": {
                "p": 5,
                "d": 1,
                "q": 0,
                "seasonal": False
            },
            "ensemble": {
                "lstm_weight": 0.3,
                "prophet_weight": 0.3,
                "xgboost_weight": 0.25,
                "arima_weight": 0.15
            }
        }
        
        # Check model type
        if model_type not in defaults:
            return False, f"Invalid model type: {model_type}", None
        
        # Get default parameters for the model type
        model_defaults = defaults[model_type]
        
        # Validate and sanitize parameters
        sanitized_params = {}
        
        # Model-specific validation
        if model_type == "lstm":
            # Lookback days
            lookback_days = params.get("lookback_days", model_defaults["lookback_days"])
            if not isinstance(lookback_days, int) or lookback_days < 5 or lookback_days > 100:
                sanitized_params["lookback_days"] = model_defaults["lookback_days"]
            else:
                sanitized_params["lookback_days"] = lookback_days
                
            # Epochs
            epochs = params.get("epochs", model_defaults["epochs"])
            if not isinstance(epochs, int) or epochs < 10 or epochs > 500:
                sanitized_params["epochs"] = model_defaults["epochs"]
            else:
                sanitized_params["epochs"] = epochs
                
            # Batch size
            batch_size = params.get("batch_size", model_defaults["batch_size"])
            if not isinstance(batch_size, int) or batch_size < 8 or batch_size > 256:
                sanitized_params["batch_size"] = model_defaults["batch_size"]
            else:
                sanitized_params["batch_size"] = batch_size
                
            # Hidden units
            hidden_units = params.get("hidden_units", model_defaults["hidden_units"])
            if not isinstance(hidden_units, int) or hidden_units < 16 or hidden_units > 512:
                sanitized_params["hidden_units"] = model_defaults["hidden_units"]
            else:
                sanitized_params["hidden_units"] = hidden_units
                
            # Dropout
            dropout = params.get("dropout", model_defaults["dropout"])
            if not isinstance(dropout, (int, float)) or dropout < 0.0 or dropout > 0.8:
                sanitized_params["dropout"] = model_defaults["dropout"]
            else:
                sanitized_params["dropout"] = dropout
                
            # Learning rate
            learning_rate = params.get("learning_rate", model_defaults["learning_rate"])
            if not isinstance(learning_rate, (int, float)) or learning_rate <= 0.0 or learning_rate > 0.1:
                sanitized_params["learning_rate"] = model_defaults["learning_rate"]
            else:
                sanitized_params["learning_rate"] = learning_rate
                
        elif model_type == "prophet":
            # Changepoint prior scale
            changepoint_prior_scale = params.get("changepoint_prior_scale", model_defaults["changepoint_prior_scale"])
            if not isinstance(changepoint_prior_scale, (int, float)) or changepoint_prior_scale <= 0.0 or changepoint_prior_scale > 0.5:
                sanitized_params["changepoint_prior_scale"] = model_defaults["changepoint_prior_scale"]
            else:
                sanitized_params["changepoint_prior_scale"] = changepoint_prior_scale
                
            # Seasonality prior scale
            seasonality_prior_scale = params.get("seasonality_prior_scale", model_defaults["seasonality_prior_scale"])
            if not isinstance(seasonality_prior_scale, (int, float)) or seasonality_prior_scale <= 0.0 or seasonality_prior_scale > 100.0:
                sanitized_params["seasonality_prior_scale"] = model_defaults["seasonality_prior_scale"]
            else:
                sanitized_params["seasonality_prior_scale"] = seasonality_prior_scale
                
            # Seasonality mode
            seasonality_mode = params.get("seasonality_mode", model_defaults["seasonality_mode"])
            if seasonality_mode not in ["additive", "multiplicative"]:
                sanitized_params["seasonality_mode"] = model_defaults["seasonality_mode"]
            else:
                sanitized_params["seasonality_mode"] = seasonality_mode
                
            # Boolean parameters
            for param in ["yearly_seasonality", "weekly_seasonality", "daily_seasonality"]:
                value = params.get(param, model_defaults[param])
                sanitized_params[param] = bool(value)
                
        elif model_type == "xgboost":
            # n_estimators
            n_estimators = params.get("n_estimators", model_defaults["n_estimators"])
            if not isinstance(n_estimators, int) or n_estimators < 10 or n_estimators > 1000:
                sanitized_params["n_estimators"] = model_defaults["n_estimators"]
            else:
                sanitized_params["n_estimators"] = n_estimators
                
            # max_depth
            max_depth = params.get("max_depth", model_defaults["max_depth"])
            if not isinstance(max_depth, int) or max_depth < 1 or max_depth > 15:
                sanitized_params["max_depth"] = model_defaults["max_depth"]
            else:
                sanitized_params["max_depth"] = max_depth
                
            # learning_rate
            learning_rate = params.get("learning_rate", model_defaults["learning_rate"])
            if not isinstance(learning_rate, (int, float)) or learning_rate <= 0.0 or learning_rate > 1.0:
                sanitized_params["learning_rate"] = model_defaults["learning_rate"]
            else:
                sanitized_params["learning_rate"] = learning_rate
                
            # subsample
            subsample = params.get("subsample", model_defaults["subsample"])
            if not isinstance(subsample, (int, float)) or subsample <= 0.0 or subsample > 1.0:
                sanitized_params["subsample"] = model_defaults["subsample"]
            else:
                sanitized_params["subsample"] = subsample
                
            # colsample_bytree
            colsample_bytree = params.get("colsample_bytree", model_defaults["colsample_bytree"])
            if not isinstance(colsample_bytree, (int, float)) or colsample_bytree <= 0.0 or colsample_bytree > 1.0:
                sanitized_params["colsample_bytree"] = model_defaults["colsample_bytree"]
            else:
                sanitized_params["colsample_bytree"] = colsample_bytree
                
            # objective
            objective = params