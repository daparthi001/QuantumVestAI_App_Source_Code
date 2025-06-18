"""
QuantumVestAI UI Utilities
Created: 2025-06-18 01:38:35
Updated: 2025-06-18 01:38:35
Author: daparthi001
"""
# This file makes the utils directory a proper Python package.
# It allows for easier imports of utility modules throughout the application.

# Import directly from local modules (without ui prefix)
from utils.formatters import (
    format_currency, 
    format_percentage, 
    format_date, 
    format_large_number, 
    format_change_value
)

from utils.validators import (
    validate_ticker_symbol,
    validate_email,
    validate_password_strength,
    validate_numeric_range,
    validate_date_range
)

from utils.helpers import (
    get_current_date,
    generate_chart_colors,
    parse_timeframe,
    calculate_percent_change,
    truncate_text
)

# This allows importing these functions directly from the utils package
# For example: from utils import format_currency, validate_email