from typing import List, Dict, Any, Union, Optional, Tuple
from datetime import datetime, timedelta
import random
import re
import json

def get_current_date(format_string: str = '%Y-%m-%d') -> str:
    """
    Get current date/time in specified format
    
    Args:
        format_string: Date format string
        
    Returns:
        Formatted date/time string
    """
    return datetime.now().strftime(format_string)

def generate_chart_colors(count: int, theme: str = 'default') -> List[str]:
    """
    Generate colors for charts based on specified theme
    
    Args:
        count: Number of colors to generate
        theme: Color theme ('default', 'dark', 'pastel', 'warm', 'cool')
        
    Returns:
        List of color hex codes
    """
    # Color palettes
    palettes = {
        'default': [
            '#4361ee', '#3a0ca3', '#4895ef', '#4cc9f0', '#560bad',
            '#f72585', '#7209b7', '#3f37c9', '#4361ee', '#4895ef'
        ],
        'dark': [
            '#03071e', '#370617', '#6a040f', '#9d0208', '#d00000',
            '#dc2f02', '#e85d04', '#f48c06', '#faa307', '#ffba08'
        ],
        'pastel': [
            '#ffadad', '#ffd6a5', '#fdffb6', '#caffbf', '#9bf6ff',
            '#a0c4ff', '#bdb2ff', '#ffc6ff', '#fffffc', '#ffd6e0'
        ],
        'warm': [
            '#ef476f', '#ffd166', '#06d6a0', '#118ab2', '#073b4c',
            '#ff595e', '#ffca3a', '#8ac926', '#1982c4', '#6a4c93'
        ],
        'cool': [
            '#5390d9', '#4ea8de', '#48bfe3', '#56cfe1', '#64dfdf',
            '#72efdd', '#80ffdb', '#34a0a4', '#168aad', '#1a759f'
        ]
    }
    
    # Get palette for theme, or default if not found
    palette = palettes.get(theme, palettes['default'])
    
    # If we need more colors than in the palette, generate them
    if count <= len(palette):
        return palette[:count]
    else:
        # Use palette colors first
        result = palette.copy()
        
        # Generate additional colors
        for i in range(count - len(palette)):
            if theme == 'pastel':
                # Pastel colors
                r = random.randint(180, 240)
                g = random.randint(180, 240)
                b = random.randint(180, 240)
            elif theme == 'dark':
                # Darker colors
                r = random.randint(20, 150)
                g = random.randint(20, 150)
                b = random.randint(20, 150)
            else:
                # Vibrant colors
                r = random.randint(50, 220)
                g = random.randint(50, 220)
                b = random.randint(50, 220)
                
            result.append(f'#{r:02x}{g:02x}{b:02x}')
            
        return result

def parse_timeframe(timeframe: str) -> Optional[Tuple[datetime, datetime]]:
    """
    Parse a timeframe string into start and end dates
    
    Args:
        timeframe: String representing timeframe ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'ytd', 'max')
        
    Returns:
        Tuple of (start_date, end_date) or None if invalid
    """
    now = datetime.now()
    
    # Handle standard timeframes
    if timeframe == '1d':
        return now - timedelta(days=1), now
    elif timeframe == '5d':
        return now - timedelta(days=5), now
    elif timeframe == '1mo':
        return now - timedelta(days=30), now
    elif timeframe == '3mo':
        return now - timedelta(days=90), now
    elif timeframe == '6mo':
        return now - timedelta(days=180), now
    elif timeframe == '1y':
        return now - timedelta(days=365), now
    elif timeframe == '2y':
        return now - timedelta(days=365*2), now
    elif timeframe == '5y':
        return now - timedelta(days=365*5), now
    elif timeframe == 'ytd':
        # Year to date (Jan 1 of current year)
        return datetime(now.year, 1, 1), now
    elif timeframe == 'max':
        # Maximum range (30 years ago)
        return now - timedelta(days=365*30), now
    
    # Try to parse custom timeframes in format 'YYYY-MM-DD..YYYY-MM-DD'
    custom_match = re.match(r'(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})', timeframe)
    if custom_match:
        try:
            start_date = datetime.strptime(custom_match.group(1), '%Y-%m-%d')
            end_date = datetime.strptime(custom_match.group(2), '%Y-%m-%d')
            return start_date, end_date
        except ValueError:
            return None
    
    # Invalid timeframe
    return None

def calculate_percent_change(old_value: Union[float, int], 
                            new_value: Union[float, int]) -> Optional[float]:
    """
    Calculate percentage change between two values
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change or None if old_value is zero
    """
    if old_value == 0:
        return None
        
    return ((new_value - old_value) / abs(old_value)) * 100

def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate text to maximum length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: String to append if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
        
    return text[:max_length - len(suffix)] + suffix

def safe_json_loads(json_str: str, default_value: Any = None) -> Any:
    """
    Safely parse JSON string
    
    Args:
        json_str: JSON string to parse
        default_value: Default value to return on error
        
    Returns:
        Parsed JSON data or default value on error
    """
    if not json_str:
        return default_value
        
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default_value

def generate_unique_id(prefix: str = '') -> str:
    """
    Generate a unique ID with optional prefix
    
    Args:
        prefix: Optional prefix string
        
    Returns:
        Unique ID string
    """
    import uuid
    unique_id = str(uuid.uuid4()).replace('-', '')[:12]
    
    if prefix:
        return f"{prefix}_{unique_id}"
    else:
        return unique_id

def get_date_range_for_period(period: str) -> Tuple[datetime, datetime]:
    """
    Get start and end dates for a specified period
    
    Args:
        period: Period identifier ('today', 'yesterday', 'this_week', 'last_week',
                'this_month', 'last_month', 'this_year', 'last_year', 'all_time')
                
    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == 'today':
        return today, today.replace(hour=23, minute=59, second=59)
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday.replace(hour=23, minute=59, second=59)
    elif period == 'this_week':
        # Start of week (Monday)
        start = today - timedelta(days=today.weekday())
        return start, today.replace(hour=23, minute=59, second=59)
    elif period == 'last_week':
        # Previous week (Monday to Sunday)
        end_of_last_week = today - timedelta(days=today.weekday() + 1)
        start_of_last_week = end_of_last_week - timedelta(days=6)
        return start_of_last_week, end_of_last_week.replace(hour=23, minute=59, second=59)
    elif period == 'this_month':
        # Start of month
        start = today.replace(day=1)
        return start, today.replace(hour=23, minute=59, second=59)
    elif period == 'last_month':
        # Previous month
        if today.month == 1:
            start = today.replace(year=today.year - 1, month=12, day=1)
        else:
            start = today.replace(month=today.month - 1, day=1)
        end = today.replace(day=1) - timedelta(days=1)
        return start, end.replace(hour=23, minute=59, second=59)
    elif period == 'this_year':
        # Start of year
        start = today.replace(month=1, day=1)
        return start, today.replace(hour=23, minute=59, second=59)
    elif period == 'last_year':
        # Previous year
        start = today.replace(year=today.year - 1, month=1, day=1)
        end = today.replace(year=today.year - 1, month=12, day=31)
        return start, end.replace(hour=23, minute=59, second=59)
    else:  # 'all_time' or any other value
        # Default to all time (30 years)
        return today - timedelta(days=365*30), today.replace(hour=23, minute=59, second=59)