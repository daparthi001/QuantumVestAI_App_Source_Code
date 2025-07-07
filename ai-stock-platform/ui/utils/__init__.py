"""
QuantumVestAI UI Utilities
Created: Original date
Updated: 2025-06-18 02:10:57
Author: daparthi001
"""
# This file makes the utils directory a proper Python package.
# It allows for easier imports of utility modules throughout the application.

# Import formatters with error handling
try:
    from utils.formatters import (
        format_currency, 
        format_percentage, 
        format_date, 
        format_large_number,
        format_change_value
    )
    __formatters_available = True
except ImportError as e:
    # Create fallback functions if formatters can't be imported
    __formatters_available = False
    
    def format_currency(value, symbol='$'):
        if value is None:
            return f"{symbol}0.00"
        try:
            return f"{symbol}{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"{symbol}0.00"
    
    def format_percentage(value, precision=2):
        if value is None:
            return f"0.{precision * '0'}%"
        try:
            return f"{float(value) * 100:.{precision}f}%"
        except (ValueError, TypeError):
            return f"0.{precision * '0'}%"
    
    def format_date(value, format_string="%Y-%m-%d"):
        if value is None:
            return "—"
        return str(value)
    
    def format_large_number(value, decimal_places=1):
        if value is None:
            return "—"
        try:
            num_value = float(value)
            if abs(num_value) >= 1e9:
                return f"{num_value / 1e9:.{decimal_places}f}B"
            elif abs(num_value) >= 1e6:
                return f"{num_value / 1e6:.{decimal_places}f}M"
            elif abs(num_value) >= 1e3:
                return f"{num_value / 1e3:.{decimal_places}f}K"
            else:
                return str(num_value)
        except (ValueError, TypeError):
            return str(value)
    
    def format_change_value(value, include_sign=True, with_color=False, decimal_places=2):
        if value is None:
            return "—"
        try:
            num_value = float(value)
            formatted = f"{num_value:.{decimal_places}f}"
            if include_sign and num_value > 0:
                formatted = f"+{formatted}"
            return formatted
        except (ValueError, TypeError):
            return str(value)

# Import validators with error handling
try:
    from utils.validators import (
        validate_ticker_symbol,
        validate_email,
        validate_password_strength,
        validate_numeric_range,
        validate_date_range
    )
    __validators_available = True
except ImportError as e:
    # Create fallback validators if validators can't be imported
    __validators_available = False
    
    def validate_ticker_symbol(ticker):
        if not ticker or len(ticker.strip()) < 1:
            return False, "Ticker symbol is required"
        return True, None
    
    def validate_email(email):
        if not email or '@' not in email:
            return False, "Valid email is required"
        return True, None
    
    def validate_password_strength(password):
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters"
        return True, None
    
    def validate_numeric_range(value, min_val=None, max_val=None):
        try:
            num_val = float(value)
            if min_val is not None and num_val < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val is not None and num_val > max_val:
                return False, f"Value must be at most {max_val}"
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid numeric value"
    
    def validate_date_range(date_val, start_date=None, end_date=None):
        return True, None  # Basic fallback

# Import helpers with error handling
try:
    from utils.helpers import (
        get_current_date,
        generate_chart_colors,
        parse_timeframe,
        calculate_percent_change,
        truncate_text
    )
    __helpers_available = True
except ImportError as e:
    # Create fallback helpers if helpers can't be imported
    __helpers_available = False
    
    def get_current_date():
        from datetime import datetime
        return datetime.now()
    
    def generate_chart_colors(count=10):
        colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', 
                 '#6f42c1', '#e83e8c', '#fd7e14', '#6c757d', '#343a40']
        return colors[:count]
    
    def parse_timeframe(timeframe):
        return timeframe
    
    def calculate_percent_change(old_value, new_value):
        if not old_value or old_value == 0:
            return 0
        try:
            return ((float(new_value) - float(old_value)) / float(old_value)) * 100
        except (ValueError, TypeError):
            return 0
    
    def truncate_text(text, length=50, suffix='...'):
        if not text:
            return ""
        text = str(text)
        return text[:length] + suffix if len(text) > length else text

# Export availability flags for debugging
__all__ = [
    'format_currency', 'format_percentage', 'format_date', 
    'format_large_number', 'format_change_value',
    'validate_ticker_symbol', 'validate_email', 'validate_password_strength',
    'validate_numeric_range', 'validate_date_range',
    'get_current_date', 'generate_chart_colors', 'parse_timeframe',
    'calculate_percent_change', 'truncate_text'
]