import re
from typing import Union, Tuple, Optional, Any, Dict
from datetime import datetime, date
import yfinance as yf

def validate_ticker_symbol(ticker: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a stock ticker symbol
    
    Args:
        ticker: The ticker symbol to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticker:
        return False, "Ticker symbol is required"
        
    # Strip whitespace and convert to uppercase
    ticker = ticker.strip().upper()
    
    # Basic pattern validation
    pattern = r'^[A-Z0-9\.]{1,6}$'
    if not re.match(pattern, ticker):
        return False, "Invalid ticker format"
        
    # Check if ticker exists (optional, may hit rate limits)
        # If yfinance lookup fails, assume ticker is valid
        # This prevents API rate limiting issues from blocking valid tickers
        return True, None

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an email address
    
    Args:
        email: The email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email address is required"
        
    # Email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
        
    return True, None

def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Args:
        password: The password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
        
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
        
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
        
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
        
    # Check for at least one digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
        
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
        
    return True, None

def validate_numeric_range(value: Union[int, float, str], 
                         min_value: Optional[Union[int, float]] = None,
                         max_value: Optional[Union[int, float]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate a numeric value against a range
    
    Args:
        value: The value to validate
        min_value: Minimum allowed value (inclusive, optional)
        max_value: Maximum allowed value (inclusive, optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, "Value is required"
        
    # Convert to numeric if string
    if isinstance(value, str):
            return False, "Value must be a number"
    
    # Check min value if specified
    if min_value is not None and value < min_value:
        return False, f"Value must be greater than or equal to {min_value}"
        
    # Check max value if specified
    if max_value is not None and value > max_value:
        return False, f"Value must be less than or equal to {max_value}"
        
    return True, None

def validate_date_range(date_value: Union[str, datetime, date],
                      min_date: Optional[Union[str, datetime, date]] = None,
                      max_date: Optional[Union[str, datetime, date]] = None,
                      date_format: str = '%Y-%m-%d') -> Tuple[bool, Optional[str]]:
    """
    Validate a date value against a range
    
    Args:
        date_value: The date to validate
        min_date: Minimum allowed date (inclusive, optional)
        max_date: Maximum allowed date (inclusive, optional)
        date_format: Format string for parsing string dates
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if date_value is None:
        return False, "Date is required"
    
    # Convert string inputs to datetime objects
    if isinstance(date_value, str):
            return False, f"Invalid date format. Expected {date_format}"
    elif isinstance(date_value, datetime):
        date_value = date_value.date()
    
    # Convert min_date if it's a string
    if isinstance(min_date, str):
            return False, f"Invalid minimum date format. Expected {date_format}"
    elif isinstance(min_date, datetime):
        min_date = min_date.date()
    
    # Convert max_date if it's a string
    if isinstance(max_date, str):
            return False, f"Invalid maximum date format. Expected {date_format}"
    elif isinstance(max_date, datetime):
        max_date = max_date.date()
    
    # Check min date if specified
    if min_date is not None and date_value < min_date:
        return False, f"Date must be on or after {min_date.strftime(date_format)}"
        
    # Check max date if specified
    if max_date is not None and date_value > max_date:
        return False, f"Date must be on or before {max_date.strftime(date_format)}"
        
    return True, None

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Tuple[bool, Optional[str]]:
    """
    Validate required fields in a data dictionary
    
    Args:
        data: Dictionary of data to validate
        required_fields: List of field names that must be present and non-empty
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        field_list = ", ".join(missing_fields)
        return False, f"Required fields missing: {field_list}"
        
    return True, None

def validate_max_length(text: str, max_length: int) -> Tuple[bool, Optional[str]]:
    """
    Validate text length does not exceed maximum
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return True, None  # Empty text is valid (unless required, which should be checked separately)
        
    if len(text) > max_length:
        return False, f"Text exceeds maximum length of {max_length} characters"
        
    return True, None
