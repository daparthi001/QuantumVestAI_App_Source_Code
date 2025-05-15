from typing import Optional, Union
from datetime import datetime
import locale

# Configure locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    pass  # Fall back to default formatting if locale not available

def format_currency(value: Union[float, int, str, None], 
                   include_symbol: bool = True, 
                   precision: int = 2,
                   default: str = 'N/A') -> str:
    """
    Format a value as currency
    
    Args:
        value: The numeric value to format
        include_symbol: Whether to include the currency symbol
        precision: Number of decimal places
        default: Default string to return for None values
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return default
        
    # Convert to float if it's a string
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return default
    
    try:
        if include_symbol:
            return f"${value:,.{precision}f}"
        else:
            return f"{value:,.{precision}f}"
    except:
        # Fallback formatting if locale fails
        if include_symbol:
            return f"${value:.{precision}f}"
        else:
            return f"{value:.{precision}f}"

def format_percentage(value: Union[float, int, str, None], 
                      include_symbol: bool = True, 
                      precision: int = 2,
                      default: str = 'N/A') -> str:
    """
    Format a value as a percentage
    
    Args:
        value: The numeric value to format (as decimal, e.g. 0.25 for 25%)
        include_symbol: Whether to include the % symbol
        precision: Number of decimal places
        default: Default string to return for None values
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return default
    
    # Convert to float if it's a string
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return default
    
    try:
        if include_symbol:
            return f"{value:.{precision}f}%"
        else:
            return f"{value:.{precision}f}"
    except:
        if include_symbol:
            return f"{value:.{precision}f}%"
        else:
            return f"{value:.{precision}f}"

def format_date(date_value: Union[str, datetime, None], 
                output_format: str = '%Y-%m-%d',
                input_format: Optional[str] = None,
                default: str = 'N/A') -> str:
    """
    Format a date value as string
    
    Args:
        date_value: Date string or datetime object
        output_format: Output date format
        input_format: Input date format (if date_value is string)
        default: Default string to return for None values
        
    Returns:
        Formatted date string
    """
    if date_value is None:
        return default
        
    try:
        if isinstance(date_value, str) and input_format:
            # Parse string to datetime using input format
            date_obj = datetime.strptime(date_value, input_format)
        elif isinstance(date_value, str):
            # Try common formats if specific format not provided
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    date_obj = datetime.strptime(date_value, fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format works
                return default
        else:
            # Assume date_value is already a datetime object
            date_obj = date_value
            
        return date_obj.strftime(output_format)
    except:
        return default

def format_large_number(value: Union[float, int, str, None],
                        precision: int = 1,
                        default: str = 'N/A') -> str:
    """
    Format large numbers with K, M, B suffixes
    
    Args:
        value: The numeric value to format
        precision: Number of decimal places
        default: Default string to return for None values
        
    Returns:
        Formatted number string with appropriate suffix
    """
    if value is None:
        return default
    
    # Convert to float if it's a string
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return default
    
    try:
        abs_value = abs(value)
        sign = '-' if value < 0 else ''
        
        if abs_value >= 1_000_000_000:
            # Billions
            return f"{sign}{abs_value / 1_000_000_000:.{precision}f}B"
        elif abs_value >= 1_000_000:
            # Millions
            return f"{sign}{abs_value / 1_000_000:.{precision}f}M"
        elif abs_value >= 1_000:
            # Thousands
            return f"{sign}{abs_value / 1_000:.{precision}f}K"
        else:
            # Regular number
            return f"{sign}{abs_value:.{precision}f}"
    except:
        return default

def format_change_value(value: Union[float, int, str, None],
                        percentage: Union[float, int, str, None] = None,
                        with_sign: bool = True,
                        with_color_class: bool = False,
                        default: str = 'N/A') -> Union[str, dict]:
    """
    Format change value with direction indicators
    
    Args:
        value: The numeric change value
        percentage: Optional percentage change value
        with_sign: Whether to include +/- sign
        with_color_class: Whether to include a color class
        default: Default string to return for None values
        
    Returns:
        Formatted change string or dict with value and class
    """
    if value is None:
        return default
    
    # Convert to float if it's a string
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return default
    
    if percentage is not None and isinstance(percentage, str):
        try:
            percentage = float(percentage)
        except ValueError:
            percentage = None
    
    try:
        # Format the value
        value_str = format_currency(value, include_symbol=False)
        
        # Add sign if requested
        if with_sign and value > 0:
            value_str = f"+{value_str}"
        
        # Add percentage if provided
        if percentage is not None:
            percentage_str = format_percentage(percentage)
            if with_sign and percentage > 0:
                percentage_str = f"+{percentage_str}"
            value_str = f"{value_str} ({percentage_str})"
        
        if with_color_class:
            # Return with appropriate CSS class
            if value > 0:
                return {"value": value_str, "class": "positive"}
            elif value < 0:
                return {"value": value_str, "class": "negative"}
            else:
                return {"value": value_str, "class": "neutral"}
        else:
            return value_str
    except:
        return default

def format_phone_number(phone: Union[str, None], 
                        format_type: str = 'national',
                        default: str = 'N/A') -> str:
    """
    Format a phone number
    
    Args:
        phone: Phone number string
        format_type: Format type ('national' or 'international')
        default: Default string to return for None values
        
    Returns:
        Formatted phone number string
    """
    if phone is None or not phone:
        return default
    
    # Clean the input
    digits = ''.join(filter(str.isdigit, phone))
    
    if len(digits) < 10:
        return default
        
    try:
        if format_type == 'international' and len(digits) >= 11:
            # International format: +X XXX XXX XXXX
            country_code = digits[0]
            area_code = digits[1:4]
            first_part = digits[4:7]
            last_part = digits[7:11]
            return f"+{country_code} {area_code} {first_part} {last_part}"
        else:
            # National format: (XXX) XXX-XXXX
            area_code = digits[-10:-7]
            first_part = digits[-7:-4]
            last_part = digits[-4:]
            return f"({area_code}) {first_part}-{last_part}"
    except:
        return phone  # Return original if formatting fails