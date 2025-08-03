"""
Services Module Initialization
Created: 2025-05-20 05:58:02
Author: daparthi001
Updated: 2025-01-09 (AI Assistant)
"""

# Import services with fallback handling for missing dependencies
try:
    from services.stock_service import StockService
    STOCK_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: StockService not available - {e}")
    StockService = None
    STOCK_SERVICE_AVAILABLE = False

try:
    from services.analytics_service import AnalyticsService
    ANALYTICS_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AnalyticsService not available - {e}")
    AnalyticsService = None
    ANALYTICS_SERVICE_AVAILABLE = False

try:
    from services.trending_stocks_service import TrendingStocksService
    TRENDING_STOCKS_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: TrendingStocksService not available - {e}")
    TrendingStocksService = None
    TRENDING_STOCKS_SERVICE_AVAILABLE = False

try:
    from services.forecast_service import ForecastService
    FORECAST_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: ForecastService not available - {e}")
    ForecastService = None
    FORECAST_SERVICE_AVAILABLE = False

try:
    from services.yahoo_rapidapi_service import YahooRapidAPIService
    YAHOO_RAPIDAPI_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: YahooRapidAPIService not available - {e}")
    YahooRapidAPIService = None
    YAHOO_RAPIDAPI_SERVICE_AVAILABLE = False

# Market overview service
try:
    from services.market_overview_service import MarketOverviewService
    MARKET_OVERVIEW_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MarketOverviewService not available - {e}")
    MarketOverviewService = None  # type: ignore
    MARKET_OVERVIEW_SERVICE_AVAILABLE = False

# Only include available services in __all__
__all__ = []
if STOCK_SERVICE_AVAILABLE:
    __all__.append('StockService')
if ANALYTICS_SERVICE_AVAILABLE:
    __all__.append('AnalyticsService')
if TRENDING_STOCKS_SERVICE_AVAILABLE:
    __all__.append('TrendingStocksService')
if FORECAST_SERVICE_AVAILABLE:
    __all__.append('ForecastService')
if YAHOO_RAPIDAPI_SERVICE_AVAILABLE:
    __all__.append('YahooRapidAPIService')
if MARKET_OVERVIEW_SERVICE_AVAILABLE:
    __all__.append('MarketOverviewService')

# New lightweight services used in tests
try:
    from services.sentiment import SentimentService
    SENTIMENT_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SentimentService not available - {e}")
    SentimentService = None  # type: ignore
    SENTIMENT_SERVICE_AVAILABLE = False

try:
    from services.prediction import PredictionService
    PREDICTION_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: PredictionService not available - {e}")
    PredictionService = None  # type: ignore
    PREDICTION_SERVICE_AVAILABLE = False

try:
    from services.ai_summary import AISummaryService
    AI_SUMMARY_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AISummaryService not available - {e}")
    AISummaryService = None  # type: ignore
    AI_SUMMARY_SERVICE_AVAILABLE = False

if SENTIMENT_SERVICE_AVAILABLE:
    __all__.append('SentimentService')
if PREDICTION_SERVICE_AVAILABLE:
    __all__.append('PredictionService')
if AI_SUMMARY_SERVICE_AVAILABLE:
    __all__.append('AISummaryService')
