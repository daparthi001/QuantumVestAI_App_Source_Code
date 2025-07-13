# Application constants

# User roles
USER_ROLE_ADMIN = "admin"
USER_ROLE_PREMIUM = "premium" 
USER_ROLE_BASIC = "basic"

# Chart types
CHART_TYPE_LINE = "line"
CHART_TYPE_CANDLESTICK = "candlestick"
CHART_TYPE_OHLC = "ohlc"
CHART_TYPE_AREA = "area"
CHART_TYPE_BAR = "bar"
CHART_TYPE_BUBBLE = "bubble"

# Chart themes
CHART_THEME_LIGHT = "light"
CHART_THEME_DARK = "dark"
CHART_THEME_QUANTUM = "quantum"

# Forecast models
MODEL_ENSEMBLE = "ensemble"
MODEL_PROPHET = "prophet"
MODEL_LSTM = "lstm"
MODEL_XGBOOST = "xgboost"
MODEL_ARIMA = "arima"
MODEL_GARCH = "garch"
MODEL_TRANSFORMER = "transformer"

# List of models available for demo forecasting
AVAILABLE_MODELS = [
    MODEL_ENSEMBLE,
    MODEL_PROPHET,
    MODEL_LSTM,
    MODEL_XGBOOST,
    MODEL_ARIMA,
]

# Default forecast periods
DEFAULT_FORECAST_DAYS = 7
MAX_FORECAST_DAYS = 90

# Default tickers for demo
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# Market indices
MARKET_INDICES = {
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC",
    "Russell 2000": "^RUT",
    "VIX": "^VIX"
}

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Technical indicators
TECHNICAL_INDICATORS = [
    "sma", "ema", "rsi", "macd", "bollinger", "stochastic", 
    "atr", "adx", "obv", "cci", "williams", "dmi"
]

# Sentiment labels
SENTIMENT_POSITIVE = "positive"
SENTIMENT_NEUTRAL = "neutral"
SENTIMENT_NEGATIVE = "negative"

# Predictability score thresholds
PREDICTABILITY_HIGH = 80
PREDICTABILITY_MEDIUM = 60
PREDICTABILITY_LOW = 40

# Analysis timeframes
TIMEFRAME_1D = "1d"
TIMEFRAME_5D = "5d"
TIMEFRAME_1M = "1mo"
TIMEFRAME_3M = "3mo"
TIMEFRAME_6M = "6mo"
TIMEFRAME_1Y = "1y"
TIMEFRAME_2Y = "2y"
TIMEFRAME_5Y = "5y"
TIMEFRAME_MAX = "max"

# API request limits
API_RATE_LIMIT = {
    "basic": 100,      # Requests per day for basic users
    "premium": 1000,   # Requests per day for premium users
    "admin": -1        # Unlimited for admins
}

# Cache keys
CACHE_KEY_MARKET_SUMMARY = "market_summary"
CACHE_KEY_STOCK_INFO = "stock_info_{ticker}"
CACHE_KEY_FORECAST = "forecast_{ticker}_{days}_{model}"

# Error messages
ERROR_API_UNAVAILABLE = "The API service is currently unavailable. Please try again later."
ERROR_INVALID_TICKER = "Invalid ticker symbol. Please enter a valid stock symbol."
ERROR_INSUFFICIENT_DATA = "Insufficient historical data for analysis."
ERROR_UNAUTHORIZED = "Authentication required. Please log in to access this feature."
ERROR_PERMISSION_DENIED = "You don't have permission to access this resource."
