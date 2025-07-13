# Template filters utility functions
# Last updated: 2025-06-20 02:50:32
# Updated by: daparthi001

import hashlib
import json
import locale
import os
import re
from datetime import datetime

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    # Fallback for environments where the locale is not available
    pass

def format_currency(value, symbol='$'):
    """Format a number as currency with proper separators and symbol.
    
    Args:
        value (float): The value to format
        symbol (str): Currency symbol to use
        
    Returns:
        str: Formatted currency string
    """
    if value is None:
        return f"{symbol}0.00"
    
        # Handle case where value cannot be converted to float
        return f"{symbol}0.00"

def format_percentage(value, precision=2):
    """Format a decimal as percentage.
    
    Args:
        value (float): The value to format (e.g., 0.1256)
        precision (int): Number of decimal places
        
    Returns:
        str: Formatted percentage (e.g., "12.56%")
    """
    if value is None:
        return f"0.{precision * '0'}%"
    
        # Handle case where value cannot be converted to float
        return f"0.{precision * '0'}%"

def truncate(s, length=50, suffix='...'):
    """Truncate a string to a specified length.
    
    Args:
        s (str): The string to truncate
        length (int): Maximum length before truncation
        suffix (str): String to append when truncated
        
    Returns:
        str: Truncated string
    """
    if s is None:
        return ""
    
    s = str(s)
    if len(s) <= length:
        return s
    else:
        return s[:length].rstrip() + suffix

def format_date(value, format_string="%b %d, %Y"):
    """Format a datetime object or ISO date string.
    
    Args:
        value: Datetime object or ISO date string
        format_string: Date format
        
    Returns:
        str: Formatted date string
    """
    if not value:
        return ""
    
    if isinstance(value, str):
                    # Return original string if parsing fails
                    return value
    
    return value.strftime(format_string)

def format_datetime(value, format_string="%b %d, %Y %H:%M"):
    """Format a datetime object or ISO datetime string with time.
    
    Args:
        value: Datetime object or ISO datetime string
        format_string: Datetime format
        
    Returns:
        str: Formatted datetime string
    """
    return format_date(value, format_string)

def relative_time(value):
    """Convert a datetime or ISO date string to a relative time string.
    
    Args:
        value: Datetime object or ISO date string
        
    Returns:
        str: Relative time (e.g., "2 hours ago", "3 days ago")
    """
    if not value:
        return ""
    
    if isinstance(value, str):
                return value
    
    now = datetime.utcnow()
    diff = now - value
    
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds // 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds // 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"

def strip_html(text):
    """Remove HTML tags from text.
    
    Args:
        text (str): Text potentially containing HTML tags
        
    Returns:
        str: Text with HTML tags removed
    """
    if not text:
        return ""
    
    return re.sub(r'<[^>]*>', '', text)

def markdown_to_html(text):
    """Convert simple markdown syntax to HTML.
    
    Args:
        text (str): Text containing markdown syntax
        
    Returns:
        str: HTML formatted text
    """
    if not text:
        return ""
    
    # Convert headers
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Convert bold and italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    # Convert links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    
    # Convert line breaks
    text = text.replace('\n\n', '<br><br>')
    
    return text

def number_format(value, decimal_places=0):
    """Format a number with thousands separators.
    
    Args:
        value: Number to format
        decimal_places: Number of decimal places
        
    Returns:
        str: Formatted number
    """
    if value is None:
        return "0"
    
        return "0"

def get_asset_url(path, version=None):
    """Generate URL for static assets with cache busting.
    
    Args:
        path (str): Asset path relative to static directory
        version (str): Optional version string for cache busting
        
    Returns:
        str: URL with cache busting parameter
    """
    # Use provided version or generate a hash based on the current date
    if not version:
        version = os.environ.get('APP_VERSION', 'v1.5.2')
    
    # Add timestamp for development environments
    if os.environ.get('ENVIRONMENT') == 'development':
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"/static/{path}?v={version}&t={timestamp}"
    
    return f"/static/{path}?v={version}"

def json_stringify(obj):
    """Convert a Python object to a JSON string.
    
    Args:
        obj: Python object to convert
        
    Returns:
        str: JSON string representation
    """
    return json.dumps(obj)

def file_size_format(size_bytes):
    """Format file size in human readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size (e.g., "2.5 MB")
    """
    if size_bytes is None:
        return "0 B"
    
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = size_bytes
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def gravatar_url(email, size=100, default='mp'):
    """Generate Gravatar URL for an email address.
    
    Args:
        email (str): User's email address
        size (int): Image size in pixels
        default (str): Default image type (mp, identicon, monsterid, wavatar, retro, robohash, blank)
        
    Returns:
        str: Gravatar URL
    """
    if not email:
        return f"https://www.gravatar.com/avatar/00000000000000000000000000000000?s={size}&d={default}"
    
    email = email.lower().strip()
    email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"

# Register all the filters
template_filters = {
    'format_currency': format_currency,
    'format_percentage': format_percentage,
    'truncate': truncate,
    'format_date': format_date,
    'format_datetime': format_datetime,
    'relative_time': relative_time,
    'strip_html': strip_html,
    'markdown_to_html': markdown_to_html,
    'number_format': number_format,
    'get_asset_url': get_asset_url,
    'json_stringify': json_stringify,
    'file_size_format': file_size_format,
    'gravatar_url': gravatar_url
}

# Function to register all filters with a Flask app
def register_filters(app):
    """Register all template filters with a Flask app.
    
    Args:
        app: Flask application instance
    """
    for name, func in template_filters.items():
        app.jinja_env.filters[name] = func

# Function to register all filters with a FastAPI Jinja2Templates
def register_jinja2_filters(templates):
    """Register all template filters with FastAPI Jinja2Templates.
    
    Args:
        templates: FastAPI Jinja2Templates instance
    """
    for name, func in template_filters.items():
        templates.env.filters[name] = func
