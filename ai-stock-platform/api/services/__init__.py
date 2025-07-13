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
