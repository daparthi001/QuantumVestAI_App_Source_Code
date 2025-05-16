"""
Utility functions for the QuantumVestAI API.

This package contains various utility functions for:
- Data loading and processing
- Feature engineering
- Data validation
- Logging helpers
"""

from api.utils.data_loader import (
    load_stock_data,
    load_market_data,
    get_ticker_info,
    get_historical_prices,
    fetch_financials,
    fetch_company_profile
)

from api.utils.feature_engineering import (
    calculate_technical_indicators,
    engineer_features,
    create_time_features,
    normalize_features,
    extract_patterns,
    calculate_volatility_metrics,
    create_lagged_features
)

from api.utils.validators import (
    validate_ticker,
    validate_date_range,
    validate_forecast_params,
    validate_model_params,
    sanitize_input,
    validate_dataframe
)

from api.utils.whitepaper_analysis import WhitepaperAnalyzer