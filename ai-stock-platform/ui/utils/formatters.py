"""
QuantumVestAI UI Formatters
Created: Original date
Updated: 2025-06-18 02:30:22
Author: daparthi001
"""
import locale
from typing import Union, Optional

# Set locale for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def format_currency(value: Union[float, int], currency_symbol: str = '$', decimal_places: int = 2) -> str:
    """Format a number as currency with specified symbol and decimal places"""
    if value is None:
        return "—"
    try:
        formatted = f"{float(value):.{decimal_places}f}"
        parts = formatted.split('.')
        integer_part = parts[0]
        decimal_part = parts[1] if len(parts) > 1 else ""
        
        # Add commas to the integer part
        if len(integer_part) > 3:
            integer_part = f"{int(integer_part):,}"
        
        if decimal_part:
            return f"{currency_symbol}{integer_part}.{decimal_part}"
        return f"{currency_symbol}{integer_part}"
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00"

def format_percentage(value: Union[float, int], decimal_places: int = 2) -> str:
    """Format a number as a percentage with specified decimal places"""
    if value is None:
        return "—"
    try:
        return f"{float(value):.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.00%"

def format_date(value, format_string: str = "%Y-%m-%d") -> str:
    """Format a date object according to the specified format string"""
    if value is None:
        return "—"
    try:
        return value.strftime(format_string)
    except (AttributeError, ValueError, TypeError):
        return str(value)

def format_large_number(value: Union[float, int], decimal_places: int = 1) -> str:
    """
    Format large numbers with K, M, B, T suffixes
    Example: 1234 -> 1.2K, 1234567 -> 1.2M
    """
    if value is None:
        return "—"
    
    try:
        value = float(value)
        abs_value = abs(value)
        sign = "-" if value < 0 else ""
        
        if abs_value >= 1e12:
            # Trillions
            return f"{sign}{abs_value/1e12:.{decimal_places}f}T"
        elif abs_value >= 1e9:
            # Billions
            return f"{sign}{abs_value/1e9:.{decimal_places}f}B"
        elif abs_value >= 1e6:
            # Millions
            return f"{sign}{abs_value/1e6:.{decimal_places}f}M"
        elif abs_value >= 1e3:
            # Thousands
            return f"{sign}{abs_value/1e3:.{decimal_places}f}K"
        else:
            # Regular number
            return f"{sign}{abs_value:.{decimal_places}f}"
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
        value = float(value)
        formatted = f"{value:.{decimal_places}f}"
        
        if include_sign and value > 0:
            formatted = f"+{formatted}"
            
        if with_color:
            if value > 0:
                return f'<span class="text-success">{formatted}</span>'
            elif value < 0:
                return f'<span class="text-danger">{formatted}</span>'
            else:
                return f'<span class="text-muted">{formatted}</span>'
        
        return formatted
    except (ValueError, TypeError):
        return str(value)