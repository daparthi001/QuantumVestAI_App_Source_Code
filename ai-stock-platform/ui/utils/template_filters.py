"""
Template filters for QuantumVestAI UI
Created: 2025-06-17 01:50:11
Updated: 2025-06-20 20:04:17
Author: daparthi001
"""

from datetime import datetime
import locale
import re
import os
import json
import hashlib

# Import additional formatter functions
try:
    # Try to import from formatters module with fallback
    from .formatters import format_large_number, format_change_value
except ImportError:
    # Fallback implementations if import fails
    def format_large_number(value, decimal_places=1):
        """Fallback implementation for format_large_number"""
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
    
    def format_change_value(value, include_sign=True, with_color=False, decimal_places=2):
        """Fallback implementation for format_change_value"""
        if value is None:
            return "—"
        try:
            num_value = float(value)
            formatted = f"{num_value:.{decimal_places}f}"
            if include_sign and num_value > 0:
                formatted = f"+{formatted}"
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

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    # Fallback for environments where the locale is not available
    pass

def format_currency(value, symbol='$'):
    """Format a number as currency with proper separators and symbol."""
    if value is None:
        return f"{symbol}0.00"
    
    try:
        # Convert to float and format
        float_value = float(value)
        return f"{symbol}{float_value:,.2f}"
    except (ValueError, TypeError):
        # Handle case where value cannot be converted to float
        return f"{symbol}0.00"

def format_percentage(value, precision=2):
    """Format a decimal as percentage."""
    if value is None:
        return f"0.{precision * '0'}%"
    
    try:
        # Convert to float and format as percentage
        float_value = float(value) * 100
        return f"{float_value:.{precision}f}%"
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

def humanize_date(value):
    """Convert a datetime or ISO date string to a human-readable relative time string.
    This is an alias for relative_time to support legacy template usage."""
    return relative_time(value)

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

def stringify(value):
    """
    Convert any value to a human-readable string representation.
    This is particularly useful for error messages and debugging.
    """
    if value is None:
        return ""
    
    if isinstance(value, dict):
        # Format dictionary as key-value pairs
        formatted_items = []
        for k, v in value.items():
            formatted_items.append(f"{k}: {stringify(v)}")
        return ", ".join(formatted_items)
    
    elif isinstance(value, list):
        # Format list items and join with commas
        formatted_items = [stringify(item) for item in value]
        return ", ".join(formatted_items)
    
    elif hasattr(value, 'items'):
        # Handle object with .items() method like dict
            pass
    
    # Default: convert to string
    return str(value)

def error_format(error_data):
    """
    Format error data specifically for display in templates.
    Handles FastAPI validation errors and other API error formats.
    """
    if not error_data:
        return ""

    html_parts = []
    
    try:
        # Process error data and format for display
        if isinstance(error_data, dict):
            for key, value in error_data.items():
                html_parts.append(f"<div class='error-item'><strong>{key}:</strong> {value}</div>")
        elif isinstance(error_data, list):
            for item in error_data:
                html_parts.append(f"<div class='error-item'>{item}</div>")
        else:
            html_parts.append(f"<div class='error-item'>{error_data}</div>")
        
        return "".join(html_parts)
    except Exception as e:
        return f"<div>Error processing error message: {str(e)}</div>"

# Dictionary of all filters
template_filters = {
    'format_currency': format_currency,
    'format_percentage': format_percentage,
    'truncate': truncate,
    'format_date': format_date,
    'format_datetime': format_datetime,
    'relative_time': relative_time,
    'humanize_date': humanize_date,
    'strip_html': strip_html,
    'markdown_to_html': markdown_to_html,
    'number_format': number_format,
    'get_asset_url': get_asset_url,
    'json_stringify': json_stringify,
    'file_size_format': file_size_format,
    'gravatar_url': gravatar_url,
    'stringify': stringify,
    'error_format': error_format,
    'format_large_number': format_large_number,  # Added missing filter
    'format_change_value': format_change_value   # Added missing filter
}

def register_filters(app):
    """
    Register all template filters with the application.
    This function is called from main.py after templates are set up.
    """
    import logging
    logger = logging.getLogger("quantumvestai_ui.filters")
    
    try:
        # Verify app and templates are available
        if not hasattr(app, 'state'):
            logger.error("App state not found")
            return False
            
        if not hasattr(app.state, 'templates'):
            logger.error("Templates not found in app state")
            return False
            
        if not hasattr(app.state.templates, 'env'):
            logger.error("Jinja2 environment not found in templates")
            return False
        
        # Register each filter with error handling
        successful_filters = 0
        failed_filters = []
        
        for name, func in template_filters.items():
            try:
                app.state.templates.env.filters[name] = func
                # CRITICAL FIX: Also add to globals so functions can be called directly in templates
                app.state.templates.env.globals[name] = func
                successful_filters += 1
                logger.debug(f"Successfully registered filter and global: {name}")
            except Exception as filter_error:
                failed_filters.append((name, str(filter_error)))
                logger.error(f"Failed to register filter {name}: {filter_error}")
        
        # Log results
        if failed_filters:
            logger.warning(f"Successfully registered {successful_filters}/{len(template_filters)} filters. "
                         f"Failed filters: {[name for name, error in failed_filters]}")
            for name, error in failed_filters:
                logger.error(f"Filter {name} error: {error}")
        else:
            logger.info(f"Successfully registered all {successful_filters} template filters and globals")
        
        # Validate critical filters are available in both filters and globals
        critical_filters = ['format_currency', 'format_percentage', 'format_change_value', 'format_large_number', 'humanize_date']
        missing_critical = []
        missing_globals = []
        
        for filter_name in critical_filters:
            if filter_name not in app.state.templates.env.filters:
                missing_critical.append(filter_name)
            if filter_name not in app.state.templates.env.globals:
                missing_globals.append(filter_name)
        
        if missing_critical:
            logger.error(f"Critical filters missing from filters: {missing_critical}")
            return False
        
        if missing_globals:
            logger.warning(f"Critical filters missing from globals (function calls may fail): {missing_globals}")
            # Don't fail for missing globals, just warn
        
        logger.info("All critical template filters are available in filters")
        if not missing_globals:
            logger.info("All critical template filters are also available in globals for function calls")
        
        return successful_filters > 0
        
    except Exception as e:
        logger.error(f"Error registering filters: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def validate_template_filters(app):
    """
    Validate that all required template filters are properly registered.
    This should be called during application startup.
    """
    import logging
    logger = logging.getLogger("quantumvestai_ui.filters")
    
    try:
        if not hasattr(app.state, 'templates') or not hasattr(app.state.templates, 'env'):
            logger.error("Templates environment not available for validation")
            return False
        
        # Define required filters for the application
        required_filters = [
            'format_currency',
            'format_percentage', 
            'format_change_value',
            'format_large_number',
            'format_date',
            'humanize_date',
            'get_asset_url'
        ]
        
        missing_filters = []
        working_filters = []
        
        for filter_name in required_filters:
            if filter_name in app.state.templates.env.filters:
                # Test the filter with sample data
                try:
                    filter_func = app.state.templates.env.filters[filter_name]
                    if filter_name == 'format_currency':
                        result = filter_func(100.50)
                    elif filter_name == 'format_percentage':
                        result = filter_func(15.75)
                    elif filter_name == 'format_change_value':
                        result = filter_func(5.25)
                    elif filter_name == 'format_large_number':
                        result = filter_func(1500000)
                    elif filter_name == 'format_date':
                        from datetime import datetime
                        result = filter_func(datetime.now())
                    elif filter_name == 'humanize_date':
                        from datetime import datetime, timedelta
                        result = filter_func(datetime.now() - timedelta(hours=1))
                    elif filter_name == 'get_asset_url':
                        result = filter_func('css/style.css')
                    
                    working_filters.append(filter_name)
                    logger.debug(f"Filter {filter_name} test successful: {result}")
                    
                except Exception as test_error:
                    logger.error(f"Filter {filter_name} failed test: {test_error}")
                    missing_filters.append(f"{filter_name} (test failed)")
            else:
                missing_filters.append(filter_name)
        
        if missing_filters:
            logger.error(f"Missing or broken required filters: {missing_filters}")
            logger.info(f"Working filters: {working_filters}")
            return False
        else:
            logger.info(f"All {len(required_filters)} required filters are working correctly")
            return True
            
    except Exception as e:
        logger.error(f"Error validating template filters: {str(e)}")
        return False


def get_template_filter_status():
    """
    Get the current status of template filters for debugging.
    Returns a dictionary with filter information.
    """
    return {
        "total_filters": len(template_filters),
        "available_filters": list(template_filters.keys()),
        "critical_filters": ['format_currency', 'format_percentage', 'format_change_value', 'format_large_number', 'humanize_date'],
        "status": "ready"
    }