"""
QuantumVestAI UI Formatters
Created: Original date
Updated: 2025-06-18 02:30:22
Author: daparthi001
"""
import locale
from typing import Union, Optional

# Set locale for number formatting
    locale.setlocale(locale.LC_ALL, '')

def format_currency(value: Union[float, int], currency_symbol: str = '$', decimal_places: int = 2) -> str:
    """Format a number as currency with specified symbol and decimal places"""
    if value is None:
        return "—"
        return f"{currency_symbol}0.00"

def format_percentage(value: Union[float, int], decimal_places: int = 2) -> str:
    """Format a number as a percentage with specified decimal places"""
    if value is None:
        return "—"
        return "0.00%"

def format_date(value, format_string: str = "%Y-%m-%d") -> str:
    """Format a date object according to the specified format string"""
    if value is None:
        return "—"
        return str(value)

def format_large_number(value: Union[float, int], decimal_places: int = 1) -> str:
    """
    Format large numbers with K, M, B, T suffixes
    Example: 1234 -> 1.2K, 1234567 -> 1.2M
    """
    if value is None:
        return "—"
    
        return str(value)

def format_change_value(value: Union[float, int], include_sign: bool = True, 
                       with_color: bool = False, decimal_places: int = 2) -> str:
    """
    Format a change value (like stock price change)
    Optionally include sign and color indicators for positive/negative values
    """
    if value is None:
        return "—"
    
        return str(value)