"""
QuantumVestAI UI Formatters
Created: 2025-06-18 01:25:07
Updated: 2025-06-18 01:25:07
Author: daparthi001
"""
import locale
from datetime import datetime
from typing import Union, Any

# Set locale for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def format_number(value: Union[int, float, None], precision: int = 0) -> str:
    """Format a number with thousands separator"""
    if value is None:
        return "N/A"
    
    try:
        if precision == 0:
            return f"{int(value):,}"
        else:
            return f"{float(value):,.{precision}f}"
    except (ValueError, TypeError):
        return str(value)

def format_market_cap(value: Union[int, float, None]) -> str:
    """Format market cap in K, M, B, T"""
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        if value >= 1_000_000_000_000:  # Trillion
            return f"${value / 1_000_000_000_000:.2f}T"
        elif value >= 1_000_000_000:  # Billion
            return f"${value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:  # Million
            return f"${value / 1_000_000:.2f}M"
        elif value >= 1_000:  # Thousand
            return f"${value / 1_000:.2f}K"
        else:
            return f"${value:.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value: Union[float, None], precision: int = 2) -> str:
    """Format a percentage value"""
    if value is None:
        return "N/A"
    
    try:
        return f"{float(value):.{precision}f}%"
    except (ValueError, TypeError):
        return str(value)

def format_currency(value: Union[float, None], symbol: str = "$", precision: int = 2) -> str:
    """Format a currency value"""
    if value is None:
        return "N/A"
    
    try:
        return f"{symbol}{float(value):,.{precision}f}"
    except (ValueError, TypeError):
        return str(value)

def format_date(value: Union[str, datetime, None], format_str: str = "%Y-%m-%d") -> str:
    """Format a date string or datetime object"""
    if value is None:
        return "N/A"
    
    try:
        if isinstance(value, str):
            # Try parsing the string as a datetime
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        
        if isinstance(value, datetime):
            return value.strftime(format_str)
        else:
            return str(value)
    except (ValueError, TypeError):
        return str(value)

def format_datetime(value: Union[str, datetime, None], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime string or datetime object"""
    return format_date(value, format_str)

def format_sentiment(value: Union[float, None]) -> str:
    """Format a sentiment score (usually between -1 and 1)"""
    if value is None:
        return "Neutral"
    
    try:
        value = float(value)
        if value > 0.6:
            return "Very Bullish"
        elif value > 0.2:
            return "Bullish"
        elif value > -0.2:
            return "Neutral"
        elif value > -0.6:
            return "Bearish"
        else:
            return "Very Bearish"
    except (ValueError, TypeError):
        return "N/A"