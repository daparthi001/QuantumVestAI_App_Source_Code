"""
Yahoo Finance Service - Import Compatibility Layer

This module provides backward compatibility for code importing from ui.services.yahoo_finance.
New code should import directly from services.yahoo_finance.
"""

# Import directly from the module to avoid circular imports
from services.yahoo_finance import YahooFinanceService

__all__ = ['YahooFinanceService']