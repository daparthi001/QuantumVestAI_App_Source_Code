"""
Template filters for QuantumVestAI UI
Created: 2025-06-17 01:50:11
Updated: 2025-06-20 03:48:17
Author: daparthi001
"""

from datetime import datetime
import locale
import re
import os
import json
import hashlib

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    # Fallback for environments where the locale is not available
    locale.setlocale(locale.LC_ALL, '')

def format_currency(value, symbol='$'):
    """Format a number as currency with proper separators and symbol."""
    if value is None:
        return f"{symbol}0.00"
    
    try:
        return f"{symbol}{locale.format_string('%,.2f', float(value), grouping=True)}"
    except (ValueError, TypeError):
        # Handle case where value cannot be converted to float
        return f"{symbol}0.00"

def format_percentage(value, precision=2):
    """Format a decimal as percentage."""
    if value is None:
        return f"0.{precision * '0'}%"
    
    try:
        # Convert to percentage and round
        percentage = float(value) * 100
        format_string = f"%.{precision}f%%"
        return format_string % percentage
    except (ValueError, TypeError):
        # Handle case where value cannot be converted to float
        return f"0.{precision * '0'}%"

def truncate(s, length=50, suffix='...'):
    """Truncate a string to a specified length."""
    if s is None:
        return ""
    
    s = str(s)
    if len(s) <= length:
        return s
    else:
        return s[:length].rstrip() + suffix

def format_date(value, format_string="%b %d, %Y"):
    """Format a datetime object or ISO date string."""
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            # Try parsing ISO format with timezone
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try parsing common formats
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    # Try parsing date only format
                    value = datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    # Return original string if parsing fails
                    return value
    
    return value.strftime(format_string)

def format_datetime(value, format_string="%b %d, %Y %H:%M"):
    """Format a datetime object or ISO datetime string with time."""
    return format_date(value, format_string)

def relative_time(value):
    """Convert a datetime or ISO date string to a relative time string."""
    if not value:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            try:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
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
    """Remove HTML tags from text."""
    if not text:
        return ""
    
    return re.sub(r'<[^>]*>', '', text)

def markdown_to_html(text):
    """Convert simple markdown syntax to HTML."""
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
    """Format a number with thousands separators."""
    if value is None:
        return "0"
    
    try:
        format_string = f"%,.{decimal_places}f"
        return locale.format_string(format_string, float(value), grouping=True)
    except (ValueError, TypeError):
        return "0"

def get_asset_url(path, version=None):
    """Generate URL for static assets with cache busting."""
    # Use provided version or generate a hash based on the current date
    if not version:
        version = os.environ.get('APP_VERSION', 'v1.5.2')
    
    # Add timestamp for development environments
    if os.environ.get('ENVIRONMENT') == 'development':
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"/static/{path}?v={version}&t={timestamp}"
    
    return f"/static/{path}?v={version}"

def json_stringify(obj):
    """Convert a Python object to a JSON string."""
    return json.dumps(obj)

def file_size_format(size_bytes):
    """Format file size in human readable format."""
    if size_bytes is None:
        return "0 B"
    
    try:
        size_bytes = float(size_bytes)
    except (ValueError, TypeError):
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = size_bytes
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def gravatar_url(email, size=100, default='mp'):
    """Generate Gravatar URL for an email address."""
    if not email:
        return f"https://www.gravatar.com/avatar/00000000000000000000000000000000?s={size}&d={default}"
    
    email = email.lower().strip()
    email_hash = hashlib.md5(email.encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"

# Dictionary of all filters
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

def register_filters(app):
    """
    Register all template filters with the application.
    This function is called from main.py after templates are set up.
    
    In FastAPI, filters need to be registered with the Jinja2Templates object,
    not with the app itself.
    """
    import logging
    logger = logging.getLogger("quantumvestai_ui.filters")
    
    try:
        # Check if app has state.templates (FastAPI approach)
        if hasattr(app, 'state') and hasattr(app.state, 'templates'):
            templates = app.state.templates
            logger.info("Registering filters with FastAPI templates")
            
            # Register all filters with the templates.env
            for name, func in template_filters.items():
                templates.env.filters[name] = func
                logger.debug(f"Registered filter: {name}")
                
            return True
        # Check if app has jinja_env directly (Flask approach)
        elif hasattr(app, 'jinja_env'):
            logger.info("Registering filters with Flask jinja_env")
            
            # Register all filters with app.jinja_env
            for name, func in template_filters.items():
                app.jinja_env.filters[name] = func
                logger.debug(f"Registered filter: {name}")
                
            return True
        else:
            # If app doesn't have templates or jinja_env, log an error
            logger.error("Cannot register filters: app has no templates attribute")
            return False
    except Exception as e:
        logger.error(f"Error registering filters: {str(e)}")
        return False