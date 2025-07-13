"""
Input Validation Module
Created: 2025-01-09
Author: AI Assistant
"""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union

from .exceptions import ValidationError


class ValidationUtils:
    """Utility class for input validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength (minimum 8 characters)"""
        if not password or not isinstance(password, str):
            return False
        return len(password) >= 8
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format (alphanumeric, underscores, hyphens)"""
        if not username or not isinstance(username, str):
            return False
        
        pattern = r'^[a-zA-Z0-9_-]{3,30}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_stock_symbol(symbol: str) -> bool:
        """Validate stock symbol format"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Stock symbols are typically 1-5 characters, letters only
        pattern = r'^[A-Z]{1,5}$'
        return re.match(pattern, symbol.upper()) is not None
    
    @staticmethod
    def validate_price(price: Union[str, float, int]) -> bool:
        """Validate price format (positive number)"""
        try:
            price_val = float(price)
            return price_val > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date_string(date_str: str) -> bool:
        """Validate date string format (YYYY-MM-DD)"""
        if not date_str or not isinstance(date_str, str):
            return False
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_pagination_params(page: int, limit: int) -> bool:
        """Validate pagination parameters"""
        return (isinstance(page, int) and page > 0 and 
                isinstance(limit, int) and 1 <= limit <= 100)


def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user registration data"""
    errors = {}
    
    # Required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    
    # Username validation
    if 'username' in data and data['username']:
        if not ValidationUtils.validate_username(data['username']):
            errors['username'] = "Username must be 3-30 characters long and contain only letters, numbers, underscores, and hyphens"
    
    # Email validation
    if 'email' in data and data['email']:
        if not ValidationUtils.validate_email(data['email']):
            errors['email'] = "Invalid email format"
    
    # Password validation
    if 'password' in data and data['password']:
        if not ValidationUtils.validate_password(data['password']):
            errors['password'] = "Password must be at least 8 characters long"
    
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return data


def validate_user_login(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user login data"""
    errors = {}
    
    # Required fields
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return data


def validate_stock_symbol_param(symbol: str) -> str:
    """Validate stock symbol parameter"""
    if not symbol:
        raise ValidationError("Stock symbol is required")
    
    if not ValidationUtils.validate_stock_symbol(symbol):
        raise ValidationError("Invalid stock symbol format")
    
    return symbol.upper()


def validate_pagination_params(page: int = 1, limit: int = 10) -> Dict[str, int]:
    """Validate pagination parameters"""
    if not ValidationUtils.validate_pagination_params(page, limit):
        raise ValidationError("Invalid pagination parameters. Page must be > 0, limit must be 1-100")
    
    return {"page": page, "limit": limit}


def validate_date_range(start_date: str, end_date: str) -> Dict[str, str]:
    """Validate date range parameters"""
    errors = {}
    
    if not ValidationUtils.validate_date_string(start_date):
        errors['start_date'] = "Invalid start date format (YYYY-MM-DD)"
    
    if not ValidationUtils.validate_date_string(end_date):
        errors['end_date'] = "Invalid end date format (YYYY-MM-DD)"
    
    if not errors:
        # Check if start date is before end date
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start > end:
            errors['date_range'] = "Start date must be before end date"
    
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return {"start_date": start_date, "end_date": end_date}


def validate_watchlist_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate watchlist data"""
    errors = {}
    
    # Required fields
    if 'name' not in data or not data['name']:
        errors['name'] = "Watchlist name is required"
    
    # Name length validation
    if 'name' in data and data['name']:
        if len(data['name']) < 1 or len(data['name']) > 100:
            errors['name'] = "Watchlist name must be 1-100 characters long"
    
    # Stocks validation
    if 'stocks' in data and data['stocks']:
        if not isinstance(data['stocks'], list):
            errors['stocks'] = "Stocks must be a list"
        else:
            for i, stock in enumerate(data['stocks']):
                if not ValidationUtils.validate_stock_symbol(stock):
                    errors[f'stocks[{i}]'] = f"Invalid stock symbol: {stock}"
    
    if errors:
        raise ValidationError(f"Validation failed: {errors}")
    
    return data


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        return str(value)
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # Truncate if too long
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize dictionary input"""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_string(item) if isinstance(item, str) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized
