"""
Utilities Module Initialization
Created: 2025-05-20 05:58:02
Author: daparthi001
"""

"""Utility module imports with graceful fallbacks."""

try:  # pragma: no cover - optional helpers may not exist
    from utils.date_utils import format_date, get_date_range, parse_date
except Exception:  # pragma: no cover - fall back to stubs
    format_date = parse_date = get_date_range = None

try:  # pragma: no cover
    from utils.market_data import get_market_data
except Exception:  # pragma: no cover
    get_market_data = None

try:  # pragma: no cover
    from utils.ml_utils import prepare_features
except Exception:  # pragma: no cover
    prepare_features = None

try:  # pragma: no cover
    from utils.validation import validate_ticker
except Exception:  # pragma: no cover
    validate_ticker = None

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "validate_email",
    "validate_password",
    "parse_date",
    "format_date",
    "calculate_metrics",
    "analyze_trend",
    "train_model",
    "predict_price",
	"get_date_range",
	"validate_ticker",
	"get_market_data",
	"prepare_features"
	
	
]
