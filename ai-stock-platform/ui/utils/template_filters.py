"""
Custom template filters for QuantumVestAI UI
Created: 2025-06-17 21:02:50
Updated: 2025-06-18 01:38:35
Author: daparthi001
"""
from fastapi import FastAPI
from jinja2 import Markup
import locale
import json
from datetime import datetime
from markupsafe import Markup
# Set locale for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, '')

def format_number(value):
    """Format large numbers with commas"""
    if value is None:
        return "—"
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value

def format_market_cap(value):
    """Format market cap with B/M suffixes"""
    if value is None:
        return "—"
    try:
        value = float(value)
        if value >= 1e12:
            return f"${value/1e12:.2f}T"
        elif value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        elif value >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    except (ValueError, TypeError):
        return value

def format_sentiment(value):
    """Format sentiment score with descriptive labels"""
    if value is None:
        return "Neutral"
    try:
        value = float(value)
        if value >= 0.7:
            return Markup(f"Very Positive <i class='fas fa-grin'></i>")
        elif value >= 0.4:
            return Markup(f"Positive <i class='fas fa-smile'></i>")
        elif value >= -0.4:
            return Markup(f"Neutral <i class='fas fa-meh'></i>")
        elif value >= -0.7:
            return Markup(f"Negative <i class='fas fa-frown'></i>")
        else:
            return Markup(f"Very Negative <i class='fas fa-angry'></i>")
    except (ValueError, TypeError):
        return "Neutral"

def time_ago(value):
    """Format datetime as time ago string"""
    if value is None:
        return ""
    try:
        if isinstance(value, str):
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        
        now = datetime.utcnow()
        diff = now - value
        
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days}d ago"
        else:
            return value.strftime("%b %d, %Y")
    except:
        return value

# Register filters with FastAPI app
def register_filters(app: FastAPI):
    """Register custom filters with FastAPI app"""
    from fastapi.templating import Jinja2Templates
    import logging
    
    # Store templates in app.state for consistency
    templates = app.state.get("templates")
    
    if templates is None:
        logging.warning("Templates not found in app.state. Using templates directly.")
        return
    
    # Access the Jinja2 environment
    env = templates.env
    
    # Register the filters
    env.filters["format_number"] = format_number
    env.filters["format_market_cap"] = format_market_cap
    env.filters["format_sentiment"] = format_sentiment
    env.filters["time_ago"] = time_ago
    env.filters["tojson"] = lambda obj: json.dumps(obj)
    
    logging.info("Template filters registered successfully")