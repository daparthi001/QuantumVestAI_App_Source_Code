"""
Enhanced Error Handling and Template Rendering System
Created: 2025-01-18
Author: AI Assistant

This module provides world-class error handling for template rendering failures,
template filter errors, and graceful degradation for missing functionality.
"""

import logging
from typing import Optional, Dict, Any, Union
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import traceback
import json

logger = logging.getLogger("quantumvestai_ui.error_handling")


class TemplateRenderingError(Exception):
    """Custom exception for template rendering errors"""
    def __init__(self, template_name: str, error: Exception, context: Optional[Dict] = None):
        self.template_name = template_name
        self.original_error = error
        self.context = context or {}
        super().__init__(f"Failed to render template '{template_name}': {str(error)}")


class EnhancedTemplateRenderer:
    """Enhanced template renderer with comprehensive error handling"""
    
    def __init__(self, templates: Jinja2Templates):
        self.templates = templates
        self.fallback_enabled = True
        self.error_count = 0
        
    def render_template_safe(
        self, 
        template_name: str, 
        context: Dict[str, Any], 
        request: Optional[Request] = None
    ) -> HTMLResponse:
        """
        Safely render a template with comprehensive error handling and fallbacks
        """
        request_id = getattr(request.state if request else None, 'request_id', 'unknown')
        
        try:
            # Ensure critical context variables are available
            enhanced_context = self._prepare_context(context, request)
            
            # Attempt template rendering
            logger.debug(f"[{request_id}] Rendering template: {template_name}")
            response = self.templates.TemplateResponse(template_name, enhanced_context)
            
            logger.debug(f"[{request_id}] Template {template_name} rendered successfully")
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"[{request_id}] Template rendering failed for {template_name}: {str(e)}")
            
            # Try to identify the specific error
            error_details = self._analyze_template_error(e, template_name, context)
            
            # Attempt fallback rendering
            return self._render_fallback(template_name, context, error_details, request)
    
    def _prepare_context(self, context: Dict[str, Any], request: Optional[Request]) -> Dict[str, Any]:
        """Prepare template context with essential variables and error handling"""
        enhanced_context = context.copy()
        
        # Ensure request is available
        if request and 'request' not in enhanced_context:
            enhanced_context['request'] = request
        
        # Add essential template functions if missing
        if 'get_asset_url' not in enhanced_context:
            enhanced_context['get_asset_url'] = self._get_safe_asset_url
        
        # Add error handling utilities
        enhanced_context['safe_format'] = self._safe_format
        enhanced_context['render_time'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        return enhanced_context
    
    def _analyze_template_error(self, error: Exception, template_name: str, context: Dict) -> Dict[str, Any]:
        """Analyze template error to provide detailed debugging information"""
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'template_name': template_name,
            'timestamp': datetime.utcnow().isoformat(),
            'context_keys': list(context.keys()) if context else []
        }
        
        # Check for specific error types
        error_str = str(error).lower()
        
        if 'no filter named' in error_str:
            # Template filter error
            filter_name = self._extract_filter_name(str(error))
            error_info['error_category'] = 'missing_filter'
            error_info['missing_filter'] = filter_name
            error_info['suggestion'] = f"Register the '{filter_name}' filter or add a fallback"
            
        elif 'template not found' in error_str or 'templatenotfound' in error_str:
            # Template not found error
            error_info['error_category'] = 'template_not_found'
            error_info['suggestion'] = f"Create template '{template_name}' or check the path"
            
        elif 'undefined' in error_str:
            # Undefined variable error
            error_info['error_category'] = 'undefined_variable'
            error_info['suggestion'] = "Check template variables and context data"
            
        else:
            error_info['error_category'] = 'unknown'
            error_info['suggestion'] = "Check template syntax and variables"
        
        return error_info
    
    def _extract_filter_name(self, error_message: str) -> Optional[str]:
        """Extract filter name from error message"""
        try:
            # Pattern: "No filter named 'filter_name'"
            if "No filter named '" in error_message:
                start = error_message.find("No filter named '") + len("No filter named '")
                end = error_message.find("'", start)
                return error_message[start:end] if end > start else None
        except Exception:
            pass
        return None
    
    def _render_fallback(
        self, 
        template_name: str, 
        context: Dict[str, Any], 
        error_details: Dict[str, Any],
        request: Optional[Request]
    ) -> HTMLResponse:
        """Render fallback HTML when template rendering fails"""
        
        if not self.fallback_enabled:
            # If fallbacks are disabled, re-raise the error
            raise TemplateRenderingError(template_name, error_details['error_message'], context)
        
        logger.warning(f"Rendering fallback for failed template: {template_name}")
        
        # Create fallback HTML based on template type
        fallback_html = self._create_fallback_html(template_name, context, error_details)
        
        return HTMLResponse(
            content=fallback_html,
            status_code=500,
            headers={
                "X-Template-Error": "true",
                "X-Original-Template": template_name,
                "X-Error-Category": error_details.get('error_category', 'unknown')
            }
        )
    
    def _create_fallback_html(self, template_name: str, context: Dict, error_details: Dict) -> str:
        """Create appropriate fallback HTML based on template name and context"""
        
        # Get basic info
        title = context.get('title', 'QuantumVestAI')
        user = context.get('user', {})
        
        # Determine template type and create appropriate fallback
        if 'login' in template_name.lower():
            return self._create_login_fallback(error_details)
        elif 'dashboard' in template_name.lower():
            return self._create_dashboard_fallback(user, error_details)
        elif 'index' in template_name.lower() or template_name == 'home.html':
            return self._create_index_fallback(error_details)
        else:
            return self._create_generic_fallback(title, template_name, error_details)
    
    def _create_login_fallback(self, error_details: Dict) -> str:
        """Create fallback login page"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Login - QuantumVestAI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h2 class="card-title text-center">QuantumVestAI Login</h2>
                                <div class="alert alert-warning">
                                    <small>Template rendering fallback active</small>
                                </div>
                                <form method="post" action="/login">
                                    <div class="mb-3">
                                        <label for="username" class="form-label">Username</label>
                                        <input type="text" class="form-control" id="username" name="username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="password" class="form-label">Password</label>
                                        <input type="password" class="form-control" id="password" name="password" required>
                                    </div>
                                    <div class="mb-3 form-check">
                                        <input type="checkbox" class="form-check-input" id="remember" name="remember">
                                        <label class="form-check-label" for="remember">Remember me</label>
                                    </div>
                                    <button type="submit" class="btn btn-primary w-100">Login</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_dashboard_fallback(self, user: Dict, error_details: Dict) -> str:
        """Create fallback dashboard page"""
        username = user.get('username', 'User')
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard - QuantumVestAI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-dark">
                <div class="container-fluid">
                    <span class="navbar-brand">QuantumVestAI</span>
                    <span class="navbar-text">Welcome, {username}</span>
                </div>
            </nav>
            <div class="container mt-4">
                <div class="alert alert-warning">
                    <h4>Dashboard Loading...</h4>
                    <p>Template rendering fallback is active. Core functionality available.</p>
                </div>
                <div class="row">
                    <div class="col-md-12">
                        <h2>Portfolio Overview</h2>
                        <p>Dashboard content will be available once template issues are resolved.</p>
                        <a href="/logout" class="btn btn-secondary">Logout</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_index_fallback(self, error_details: Dict) -> str:
        """Create fallback index page"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>QuantumVestAI - AI-Powered Investment Platform</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-primary">
                <div class="container">
                    <span class="navbar-brand">QuantumVestAI</span>
                    <div>
                        <a href="/login" class="btn btn-light btn-sm">Login</a>
                        <a href="/register" class="btn btn-outline-light btn-sm">Register</a>
                    </div>
                </div>
            </nav>
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="display-4">Welcome to QuantumVestAI</h1>
                    <p class="lead">AI-Powered Investment Platform</p>
                    <div class="alert alert-info">
                        <p>Platform is running in fallback mode. Please contact support if issues persist.</p>
                    </div>
                    <a href="/login" class="btn btn-primary btn-lg">Get Started</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_generic_fallback(self, title: str, template_name: str, error_details: Dict) -> str:
        """Create generic fallback page"""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="text-center">
                    <h1>Page Temporarily Unavailable</h1>
                    <p class="lead">We're experiencing technical difficulties with this page.</p>
                    <div class="alert alert-warning">
                        <p>Template: {template_name}</p>
                        <p>Error: {error_details.get('error_category', 'unknown')}</p>
                    </div>
                    <a href="/" class="btn btn-primary">Go Home</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_safe_asset_url(self, path: str, version: str = None) -> str:
        """Safe asset URL generator with fallback"""
        try:
            if not version:
                version = "v1.0.0"
            return f"/static/{path}?v={version}"
        except Exception:
            return f"/static/{path}"
    
    def _safe_format(self, value: Any, format_type: str = "string") -> str:
        """Safe formatting function for templates"""
        try:
            if format_type == "currency" and isinstance(value, (int, float)):
                return f"${value:,.2f}"
            elif format_type == "percentage" and isinstance(value, (int, float)):
                return f"{value:.2f}%"
            elif format_type == "large_number" and isinstance(value, (int, float)):
                if abs(value) >= 1e9:
                    return f"{value / 1e9:.1f}B"
                elif abs(value) >= 1e6:
                    return f"{value / 1e6:.1f}M"
                elif abs(value) >= 1e3:
                    return f"{value / 1e3:.1f}K"
                else:
                    return f"{value:.2f}"
            else:
                return str(value)
        except Exception:
            return str(value) if value is not None else ""


# Global instance for easy access
_enhanced_renderer: Optional[EnhancedTemplateRenderer] = None


def get_enhanced_renderer(templates: Jinja2Templates) -> EnhancedTemplateRenderer:
    """Get or create enhanced template renderer"""
    global _enhanced_renderer
    if _enhanced_renderer is None:
        _enhanced_renderer = EnhancedTemplateRenderer(templates)
    return _enhanced_renderer


def create_error_response(
    error: Exception, 
    request: Request, 
    template_name: str = None,
    fallback_title: str = "Error"
) -> HTMLResponse:
    """Create user-friendly error response"""
    
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"[{request_id}] Creating error response for: {str(error)}")
    
    error_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error - QuantumVestAI</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card border-danger">
                        <div class="card-header bg-danger text-white">
                            <h4>Service Temporarily Unavailable</h4>
                        </div>
                        <div class="card-body">
                            <p class="lead">We're experiencing technical difficulties. Please try again later.</p>
                            <div class="alert alert-info">
                                <strong>What you can do:</strong>
                                <ul class="mb-0">
                                    <li>Refresh the page in a few moments</li>
                                    <li>Clear your browser cache</li>
                                    <li>Contact support if the problem persists</li>
                                </ul>
                            </div>
                            <div class="mt-3">
                                <a href="/" class="btn btn-primary">Go Home</a>
                                <button onclick="location.reload()" class="btn btn-secondary">Retry</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(
        content=error_html,
        status_code=500,
        headers={
            "X-Error-Handler": "enhanced",
            "X-Request-ID": request_id
        }
    )