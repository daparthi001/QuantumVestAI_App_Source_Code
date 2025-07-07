"""
QuantumVestAI UI Formatters
Created: Original date
Updated: 2025-06-18 02:30:22
Author: daparthi001
"""
import locale
from typing import Union, Optional

# Set locale for number formatting with error handling
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    # Fallback to 'C' locale if system locale is not available
    locale.setlocale(locale.LC_ALL, 'C')

def format_currency(value: Union[float, int], currency_symbol: str = '$', decimal_places: int = 2) -> str:
    """Format a number as currency with specified symbol and decimal places"""
    if value is None:
        return "—"
    
    try:
        # Format with locale-aware thousands separators
        formatted = locale.format_string(f"%.{decimal_places}f", float(value), grouping=True)
        return f"{currency_symbol}{formatted}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"

def format_percentage(value: Union[float, int], decimal_places: int = 2) -> str:
    """Format a number as a percentage with specified decimal places"""
    if value is None:
        return "—"
    
    try:
        formatted = f"{float(value):.{decimal_places}f}%"
        return formatted
    except (ValueError, TypeError):
        return "0.00%"

def format_date(value, format_string: str = "%Y-%m-%d") -> str:
    """Format a date object according to the specified format string"""
    if value is None:
        return "—"
    
    try:
        from datetime import datetime
        
        # Handle different input types
        if isinstance(value, str):
            # Try to parse string date
            date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
        elif hasattr(value, 'strftime'):
            # Already a date/datetime object
            date_obj = value
        else:
            return str(value)
        
        return date_obj.strftime(format_string)
    except (ValueError, TypeError, AttributeError):
        return str(value)

def format_large_number(value: Union[float, int], decimal_places: int = 1) -> str:
    """
    Format large numbers with K, M, B, T suffixes
    Example: 1234 -> 1.2K, 1234567 -> 1.2M
    """
    if value is None:
        return "—"
    
    try:
        num_value = float(value)
        
        if abs(num_value) >= 1e12:
            return f"{num_value / 1e12:.{decimal_places}f}T"
        elif abs(num_value) >= 1e9:
            return f"{num_value / 1e9:.{decimal_places}f}B"
        elif abs(num_value) >= 1e6:
            return f"{num_value / 1e6:.{decimal_places}f}M"
        elif abs(num_value) >= 1e3:
            return f"{num_value / 1e3:.{decimal_places}f}K"
        else:
            return str(num_value)
    except (ValueError, TypeError):
        return str(value)

def format_change_value(value: Union[float, int], include_sign: bool = True, 
                       with_color: bool = False, decimal_places: int = 2) -> str:
    """
    Format a change value (like stock price change)
    Optionally include sign and color indicators for positive/negative values
    """
    if value is None:
        return "—"
    
    try:
        num_value = float(value)
        
        # Format the number
        formatted = f"{num_value:.{decimal_places}f}"
        
        # Add sign if requested and value is positive
        if include_sign and num_value > 0:
            formatted = f"+{formatted}"
        
        # Add color indicators if requested
        if with_color:
            if num_value > 0:
                formatted = f"🟢 {formatted}"
            elif num_value < 0:
                formatted = f"🔴 {formatted}"
            else:
                formatted = f"⚪ {formatted}"
        
        return formatted
    except (ValueError, TypeError):
        return str(value)