"""
Utility functions for feature engineering.

These functions implement various feature engineering techniques
for time series data, particularly for stock price data.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

logger = logging.getLogger("api")

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply a comprehensive set of feature engineering techniques.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with engineered features
    """
    try:
        # Make a copy to avoid modifying the original
        df_features = df.copy()
        
        # Ensure date column is datetime
        if "date" in df_features.columns:
            df_features["date"] = pd.to_datetime(df_features["date"])
        
        # Add price-based features
        df_features = calculate_technical_indicators(df_features)
        
        # Add time-based features
        df_features = create_time_features(df_features)
        
        # Add lagged features
        df_features = create_lagged_features(df_features)
        
        # Add volatility metrics
        df_features = calculate_volatility_metrics(df_features)
        
        # Add pattern recognition features
        df_features = extract_patterns(df_features)
        
        # Fill NaN values with appropriate methods
        df_features = _fill_missing_values(df_features)
        
        return df_features
        
    except Exception as e:
        logger.exception(f"Error in feature engineering: {e}")
        # Return original dataframe if error occurs
        return df

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate common technical indicators.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with technical indicators
    """
    try:
        # Make a copy to avoid modifying the original
        df_tech = df.copy()
        
        # Simple Moving Averages (SMA)
        for window in [5, 10, 20, 50, 200]:
            df_tech[f'ma{window}'] = df_tech['close'].rolling(window=window).mean()
        
        # Exponential Moving Averages (EMA)
        for window in [5, 10, 20, 50, 200]:
            df_tech[f'ema{window}'] = df_tech['close'].ewm(span=window, adjust=False).mean()
        
        # Moving Average Convergence Divergence (MACD)
        df_tech['ema12'] = df_tech['close'].ewm(span=12, adjust=False).mean()
        df_tech['ema26'] = df_tech['close'].ewm(span=26, adjust=False).mean()
        df_tech['macd'] = df_tech['ema12'] - df_tech['ema26']
        df_tech['macd_signal'] = df_tech['macd'].ewm(span=9, adjust=False).mean()
        df_tech['macd_hist'] = df_tech['macd'] - df_tech['macd_signal']
        
        # Relative Strength Index (RSI)
        delta = df_tech['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        
        rs = avg_gain / avg_loss
        df_tech['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df_tech['bb_middle'] = df_tech['close'].rolling(window=20).mean()
        stddev = df_tech['close'].rolling(window=20).std()
        df_tech['bb_upper'] = df_tech['bb_middle'] + 2 * stddev
        df_tech['bb_lower'] = df_tech['bb_middle'] - 2 * stddev
        df_tech['bb_width'] = (df_tech['bb_upper'] - df_tech['bb_lower']) / df_tech['bb_middle']
        df_tech['bb_pct'] = (df_tech['close'] - df_tech['bb_lower']) / (df_tech['bb_upper'] - df_tech['bb_lower'])
        
        # Stochastic Oscillator
        n = 14
        df_tech['stoch_k'] = 100 * ((df_tech['close'] - df_tech['low'].rolling(window=n).min()) / 
                              (df_tech['high'].rolling(window=n).max() - df_tech['low'].rolling(window=n).min()))
        df_tech['stoch_d'] = df_tech['stoch_k'].rolling(window=3).mean()
        
        # Average True Range (ATR)
        high_low = df_tech['high'] - df_tech['low']
        high_close = np.abs(df_tech['high'] - df_tech['close'].shift())
        low_close = np.abs(df_tech['low'] - df_tech['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df_tech['atr'] = true_range.rolling(window=14).mean()
        df_tech['atr_pct'] = df_tech['atr'] / df_tech['close']
        
        # On-Balance Volume (OBV)
        df_tech['obv'] = (np.sign(df_tech['close'].diff()) * df_tech['volume']).fillna(0).cumsum()
        
        # Price Rate of Change (ROC)
        for window in [5, 10, 20]:
            df_tech[f'roc{window}'] = df_tech['close'].pct_change(periods=window) * 100
        
        # Commodity Channel Index (CCI)
        typical_price = (df_tech['high'] + df_tech['low'] + df_tech['close']) / 3
        mean_dev = abs(typical_price - typical_price.rolling(window=20).mean()).rolling(window=20).mean()
        df_tech['cci'] = (typical_price - typical_price.rolling(window=20).mean()) / (0.015 * mean_dev)
        
        # Average Directional Index (ADX)
        plus_dm = df_tech['high'].diff()
        minus_dm = -df_tech['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        plus_dm[plus_dm < minus_dm] = 0
        minus_dm[minus_dm < plus_dm] = 0
        
        tr = true_range
        plus_di = 100 * plus_dm.rolling(window=14).mean() / tr.rolling(window=14).mean()
        minus_di = 100 * minus_dm.rolling(window=14).mean() / tr.rolling(window=14).mean()
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df_tech['adx'] = dx.rolling(window=14).mean()
        df_tech['plus_di'] = plus_di
        df_tech['minus_di'] = minus_di
        
        # Money Flow Index (MFI)
        typical_price = (df_tech['high'] + df_tech['low'] + df_tech['close']) / 3
        money_flow = typical_price * df_tech['volume']
        
        positive_flow = money_flow.copy()
        negative_flow = money_flow.copy()
        
        positive_flow[typical_price < typical_price.shift(1)] = 0
        negative_flow[typical_price > typical_price.shift(1)] = 0
        
        positive_mf = positive_flow.rolling(window=14).sum()
        negative_mf = negative_flow.rolling(window=14).sum()
        
        money_ratio = positive_mf / negative_mf
        df_tech['mfi'] = 100 - (100 / (1 + money_ratio))
        
        # Price and Volume Trends
        df_tech['price_volume'] = df_tech['close'] * df_tech['volume']
        df_tech['price_volume_ma'] = df_tech['price_volume'].rolling(window=20).mean()
        
        return df_tech
        
    except Exception as e:
        logger.exception(f"Error calculating technical indicators: {e}")
        # Return original dataframe if error occurs
        return df

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create time-based features from date column.
    
    Args:
        df: DataFrame with date column
        
    Returns:
        DataFrame with time features
    """
    try:
        # Make a copy to avoid modifying the original
        df_time = df.copy()
        
        # Ensure date column is datetime
        if "date" in df_time.columns:
            df_time["date"] = pd.to_datetime(df_time["date"])
            
            # Extract basic time components
            df_time["year"] = df_time["date"].dt.year
            df_time["month"] = df_time["date"].dt.month
            df_time["day"] = df_time["date"].dt.day
            df_time["day_of_week"] = df_time["date"].dt.dayofweek
            df_time["day_of_year"] = df_time["date"].dt.dayofyear
            df_time["week_of_year"] = df_time["date"].dt.isocalendar().week
            df_time["quarter"] = df_time["date"].dt.quarter
            
            # Binary features
            df_time["is_month_end"] = df_time["date"].dt.is_month_end.astype(int)
            df_time["is_month_start"] = df_time["date"].dt.is_month_start.astype(int)
            df_time["is_quarter_end"] = df_time["date"].dt.is_quarter_end.astype(int)
            df_time["is_quarter_start"] = df_time["date"].dt.is_quarter_start.astype(int)
            df_time["is_year_end"] = df_time["date"].dt.is_year_end.astype(int)
            df_time["is_year_start"] = df_time["date"].dt.is_year_start.astype(int)
            
            # Cyclical encoding for day of week and month
            df_time["day_of_week_sin"] = np.sin(2 * np.pi * df_time["day_of_week"] / 7)
            df_time["day_of_week_cos"] = np.cos(2 * np.pi * df_time["day_of_week"] / 7)
            df_time["month_sin"] = np.sin(2 * np.pi * df_time["month"] / 12)
            df_time["month_cos"] = np.cos(2 * np.pi * df_time["month"] / 12)
            
        return df_time
        
    except Exception as e:
        logger.exception(f"Error creating time features: {e}")
        # Return original dataframe if error occurs
        return df

def create_lagged_features(df: pd.DataFrame, lag_periods: List[int] = [1, 2, 3, 5, 10]) -> pd.DataFrame:
    """
    Create lagged features for key columns.
    
    Args:
        df: DataFrame with time series data
        lag_periods: List of lag periods to create
        
    Returns:
        DataFrame with lagged features
    """
    try:
        # Make a copy to avoid modifying the original
        df_lag = df.copy()
        
        # Columns to create lags for
        lag_columns = ['close', 'volume']
        
        # Add additional columns if they exist
        potential_columns = ['rsi', 'macd', 'bb_width', 'atr']
        for col in potential_columns:
            if col in df_lag.columns:
                lag_columns.append(col)
        
        # Create lags
        for col in lag_columns:
            if col in df_lag.columns:
                for lag in lag_periods:
                    df_lag[f'{col}_lag{lag}'] = df_lag[col].shift(lag)
        
        # Create percentage changes
        for col in ['close', 'volume']:
            if col in df_lag.columns:
                for lag in lag_periods:
                    df_lag[f'{col}_pct{lag}'] = df_lag[col].pct_change(periods=lag)
        
        # Create rolling features
        for window in [5, 10, 20]:
            if 'close' in df_lag.columns:
                df_lag[f'close_min{window}'] = df_lag['close'].rolling(window=window).min()
                df_lag[f'close_max{window}'] = df_lag['close'].rolling(window=window).max()
                df_lag[f'close_range{window}'] = df_lag[f'close_max{window}'] - df_lag[f'close_min{window}']
        
        return df_lag
        
    except Exception as e:
        logger.exception(f"Error creating lagged features: {e}")
        # Return original dataframe if error occurs
        return df

def normalize_features(
    df: pd.DataFrame, 
    method: str = 'standard', 
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Normalize features using specified method.
    
    Args:
        df: DataFrame with features
        method: Normalization method ('standard', 'minmax')
        columns: List of columns to normalize (all numeric if None)
        
    Returns:
        DataFrame with normalized features
    """
    try:
        # Make a copy to avoid modifying the original
        df_norm = df.copy()
        
        # Select columns to normalize
        if columns is None:
            # Skip date and ticker columns
            exclude_cols = ['date', 'ticker']
            columns = [col for col in df_norm.columns if col not in exclude_cols and np.issubdtype(df_norm[col].dtype, np.number)]
        
        # Select scaler based on method
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        # Apply normalization
        if columns:
            df_norm[columns] = scaler.fit_transform(df_norm[columns])
        
        return df_norm
        
    except Exception as e:
        logger.exception(f"Error normalizing features: {e}")
        # Return original dataframe if error occurs
        return df

def extract_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract common candlestick patterns.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with pattern features
    """
    try:
        # Make a copy to avoid modifying the original
        df_patterns = df.copy()
        
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in df_patterns.columns for col in required_cols):
            return df
        
        # Calculate basic candlestick properties
        df_patterns['body_size'] = abs(df_patterns['close'] - df_patterns['open'])
        df_patterns['shadow_upper'] = df_patterns['high'] - np.maximum(df_patterns['open'], df_patterns['close'])
        df_patterns['shadow_lower'] = np.minimum(df_patterns['open'], df_patterns['close']) - df_patterns['low']
        df_patterns['body_to_range'] = df_patterns['body_size'] / (df_patterns['high'] - df_patterns['low'])
        df_patterns['is_bullish'] = (df_patterns['close'] > df_patterns['open']).astype(int)
        
        # Average body size
        avg_body = df_patterns['body_size'].rolling(window=10).mean()
        
        # Doji (very small body)
        df_patterns['is_doji'] = (df_patterns['body_size'] < 0.1 * avg_body).astype(int)
        
        # Hammer (small body, long lower shadow, small upper shadow)
        df_patterns['is_hammer'] = ((df_patterns['body_size'] < 0.5 * (df_patterns['high'] - df_patterns['low'])) &
                                  (df_patterns['shadow_lower'] > 2 * df_patterns['body_size']) &
                                  (df_patterns['shadow_upper'] < df_patterns['body_size'])).astype(int)
        
        # Shooting Star (small body, long upper shadow, small lower shadow)
        df_patterns['is_shooting_star'] = ((df_patterns['body_size'] < 0.5 * (df_patterns['high'] - df_patterns['low'])) &
                                         (df_patterns['shadow_upper'] > 2 * df_patterns['body_size']) &
                                         (df_patterns['shadow_lower'] < df_patterns['body_size'])).astype(int)
        
        # Engulfing patterns
        df_patterns['is_bullish_engulfing'] = ((df_patterns['close'].shift(1) < df_patterns['open'].shift(1)) & 
                                             (df_patterns['close'] > df_patterns['open']) &
                                             (df_patterns['close'] > df_patterns['open'].shift(1)) &
                                             (df_patterns['open'] < df_patterns['close'].shift(1))).astype(int)
        
        df_patterns['is_bearish_engulfing'] = ((df_patterns['close'].shift(1) > df_patterns['open'].shift(1)) & 
                                             (df_patterns['close'] < df_patterns['open']) &
                                             (df_patterns['close'] < df_patterns['open'].shift(1)) &
                                             (df_patterns['open'] > df_patterns['close'].shift(1))).astype(int)
        
        # Morning Star and Evening Star (3-day patterns)
        df_patterns['is_morning_star'] = ((df_patterns['close'].shift(2) < df_patterns['open'].shift(2)) &
                                        (df_patterns['body_size'].shift(1) < 0.5 * df_patterns['body_size'].shift(2)) &
                                        (df_patterns['close'] > df_patterns['open']) &
                                        (df_patterns['close'] > (df_patterns['open'].shift(2) + 
                                                               df_patterns['close'].shift(2)) / 2)).astype(int)
        
        df_patterns['is_evening_star'] = ((df_patterns['close'].shift(2) > df_patterns['open'].shift(2)) &
                                        (df_patterns['body_size'].shift(1) < 0.5 * df_patterns['body_size'].shift(2)) &
                                        (df_patterns['close'] < df_patterns['open']) &
                                        (df_patterns['close'] < (df_patterns['open'].shift(2) + 
                                                               df_patterns['close'].shift(2)) / 2)).astype(int)
        
        # Price gaps
        df_patterns['gap_up'] = ((df_patterns['low'] > df_patterns['high'].shift(1))).astype(int)
        df_patterns['gap_down'] = ((df_patterns['high'] < df_patterns['low'].shift(1))).astype(int)
        
        return df_patterns
        
    except Exception as e:
        logger.exception(f"Error extracting patterns: {e}")
        # Return original dataframe if error occurs
        return df

def calculate_volatility_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate volatility metrics.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        DataFrame with volatility metrics
    """
    try:
        # Make a copy to avoid modifying the original
        df_vol = df.copy()
        
        # Daily returns
        if 'close' in df_vol.columns:
            df_vol['daily_return'] = df_vol['close'].pct_change()
            df_vol['log_return'] = np.log(df_vol['close'] / df_vol['close'].shift(1))
            
            # Historical volatility (standard deviation of returns)
            for window in [5, 10, 20, 30]:
                df_vol[f'volatility_{window}d'] = df_vol['log_return'].rolling(window=window).std() * np.sqrt(252)
            
            # Parkinson volatility (uses high-low range)
            if all(col in df_vol.columns for col in ['high', 'low']):
                df_vol['parkinson'] = np.sqrt(1 / (4 * np.log(2)) * 
                                           ((np.log(df_vol['high'] / df_vol['low']) ** 2).rolling(window=20).mean()) * 
                                           252)
            
            # Garman-Klass volatility (uses OHLC)
            if all(col in df_vol.columns for col in ['open', 'high', 'low', 'close']):
                df_vol['garman_klass'] = np.sqrt(
                    (0.5 * np.log(df_vol['high'] / df_vol['low']) ** 2 - 
                     (2 * np.log(2) - 1) * np.log(df_vol['close'] / df_vol['open']) ** 2
                    ).rolling(window=20).mean() * 252
                )
            
            # GARCH-like volatility estimate (simplified)
            df_vol['sq_return'] = df_vol['log_return'] ** 2
            df_vol['ewma_variance'] = df_vol['sq_return'].ewm(alpha=0.06).mean()
            df_vol['ewma_volatility'] = np.sqrt(df_vol['ewma_variance'] * 252)
            
            # Volatility ratio (short-term to long-term)
            df_vol['volatility_ratio'] = df_vol['volatility_10d'] / df_vol['volatility_30d']
            
        return df_vol
        
    except Exception as e:
        logger.exception(f"Error calculating volatility metrics: {e}")
        # Return original dataframe if error occurs
        return df

def _fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values using appropriate methods for each column type.
    
    Args:
        df: DataFrame with potential missing values
        
    Returns:
        DataFrame with filled values
    """
    try:
        # Make a copy
        df_filled = df.copy()
        
        # Skip non-numeric columns
        numeric_cols = df_filled.select_dtypes(include=np.number).columns
        
        for col in numeric_cols:
            # Use forward fill for most columns
            df_filled[col] = df_filled[col].fillna(method='ffill')
            
            # Use backward fill as a backup
            df_filled[col] = df_filled[col].fillna(method='bfill')
            
            # Use median as a last resort
            df_filled[col] = df_filled[col].fillna(df_filled[col].median() if not df_filled[col].isna().all() else 0)
        
        return df_filled
        
    except Exception as e:
        logger.exception(f"Error filling missing values: {e}")
        # Return original dataframe if error occurs
        return df
