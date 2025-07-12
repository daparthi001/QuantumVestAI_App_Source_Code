"""
Template Context Processor for QuantumVestAI UI
Created: 2025-01-13
Author: AI Assistant

Provides common template context variables and utilities for all templates.
This ensures consistent availability of essential variables like `now`, `user`, etc.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("quantumvestai_ui.template_context")


class TemplateContextProcessor:
    """
    Centralized template context processor for adding common variables
    to all template contexts throughout the application.
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize the context processor.
        
        Args:
            api_url: Optional API URL to include in context
        """
        self.api_url = api_url or os.environ.get("API_URL", "http://api:8000")
        logger.info(f"Template context processor initialized with API_URL: {self.api_url}")
    
    def get_base_context(self) -> Dict[str, Any]:
        """
        Get the base context variables that should be available in all templates.
        
        Returns:
            Dictionary of context variables
        """
        return {
            # Current date/time functions
            "now": datetime.utcnow,  # Function that returns current UTC time
            "current_year": datetime.utcnow().year,
            
            # API configuration
            "API_URL": self.api_url,
            "API_V1_URL": f"{self.api_url}/api/v1",
            
            # Application metadata
            "app_version": os.environ.get("APP_VERSION", "2.0.0"),
            "app_name": "QuantumVestAI",
            "app_description": "AI-Powered Investment Platform",
            
            # Feature flags
            "debug_mode": os.environ.get("DEBUG", "false").lower() == "true",
            "demo_mode": os.environ.get("DEMO_MODE", "true").lower() == "true",
            
            # Time helpers
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def add_user_context(self, context: Dict[str, Any], user_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add user-specific context variables.
        
        Args:
            context: Existing context dictionary
            user_data: Optional user data dictionary
            
        Returns:
            Updated context dictionary
        """
        if user_data:
            context.update({
                "user": user_data,
                "is_authenticated": True,
                "user_name": user_data.get("username", "Guest"),
                "user_email": user_data.get("email", ""),
            })
        else:
            context.update({
                "user": None,
                "is_authenticated": False,
                "user_name": "Guest",
                "user_email": "",
            })
        
        return context
    
    def add_request_context(self, context: Dict[str, Any], request) -> Dict[str, Any]:
        """
        Add request-specific context variables.
        
        Args:
            context: Existing context dictionary
            request: FastAPI Request object
            
        Returns:
            Updated context dictionary
        """
        context.update({
            "request": request,
            "request_path": request.url.path,
            "request_method": request.method,
            "request_id": getattr(request.state, 'request_id', 'unknown'),
        })
        
        return context
    
    def create_template_context(self, request, user_data: Optional[Dict] = None, **extra_context) -> Dict[str, Any]:
        """
        Create a complete template context with all common variables.
        
        Args:
            request: FastAPI Request object
            user_data: Optional user data dictionary
            **extra_context: Additional context variables
            
        Returns:
            Complete template context dictionary
        """
        # Start with base context
        context = self.get_base_context()
        
        # Add user context
        context = self.add_user_context(context, user_data)
        
        # Add request context
        context = self.add_request_context(context, request)
        
        # Add any extra context
        context.update(extra_context)
        
        return context


def setup_template_globals(jinja_env, api_url: Optional[str] = None):
    """
    Set up global template variables in Jinja2 environment.
    
    Args:
        jinja_env: Jinja2 Environment object
        api_url: Optional API URL
    """
    processor = TemplateContextProcessor(api_url)
    base_context = processor.get_base_context()
    
    # Add base context variables as globals
    for key, value in base_context.items():
        jinja_env.globals[key] = value
    
    # Add utility functions as globals
    jinja_env.globals["get_current_year"] = lambda: datetime.utcnow().year
    jinja_env.globals["format_datetime"] = lambda dt, fmt="%Y-%m-%d %H:%M:%S": dt.strftime(fmt) if dt else ""
    
    logger.info(f"✓ Template globals configured: {list(base_context.keys())}")


def create_safe_template_context(request, templates, template_name: str, **context_vars) -> Dict[str, Any]:
    """
    Create a safe template context with error handling and fallbacks.
    
    Args:
        request: FastAPI Request object
        templates: Jinja2Templates instance
        template_name: Name of the template being rendered
        **context_vars: Additional context variables
        
    Returns:
        Safe template context dictionary with fallbacks
    """
    try:
        processor = TemplateContextProcessor()
        context = processor.create_template_context(request, **context_vars)
        
        # Add template-specific metadata
        context.update({
            "template_name": template_name,
            "render_time": datetime.utcnow(),
        })
        
        return context
        
    except Exception as e:
        logger.error(f"Error creating template context for {template_name}: {e}")
        
        # Return minimal safe context as fallback
        return {
            "request": request,
            "now": datetime.utcnow,
            "current_year": datetime.utcnow().year,
            "app_name": "QuantumVestAI",
            "template_name": template_name,
            "error_mode": True,
            **context_vars
        }


# Global context processor instance
_global_processor = None

def get_global_context_processor() -> TemplateContextProcessor:
    """Get or create the global context processor instance."""
    global _global_processor
    if _global_processor is None:
        _global_processor = TemplateContextProcessor()
    return _global_processor
