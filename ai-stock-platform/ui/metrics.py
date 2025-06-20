"""
Prometheus metrics for QuantumVestAI UI
Created: 2025-06-20 03:52:02
Author: daparthi001

This module provides Prometheus metrics for monitoring the application.
"""

from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total', 
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds', 
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30, 60]
)

active_users_gauge = Gauge(
    'active_users',
    'Number of active users currently using the application'
)

api_request_duration_seconds = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.05, 0.1, 0.5, 1, 5, 10, 30]
)

# Function to track request duration
def track_request_duration(method, endpoint):
    """
    Context manager to track HTTP request duration.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Request endpoint path
        
    Returns:
        A context manager that measures request duration
    """
    class TimerContextManager:
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    return TimerContextManager()

# Function to track API request duration
def track_api_request_duration(method, endpoint):
    """
    Context manager to track API request duration.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        
    Returns:
        A context manager that measures API request duration
    """
    class TimerContextManager:
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            api_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    return TimerContextManager()

# Function to increment request count
def increment_request_count(method, endpoint, status_code):
    """
    Increment the HTTP request counter.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: Request endpoint path
        status_code: HTTP status code
    """
    http_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).inc()

# User tracking
def user_logged_in():
    """
    Increment the active users gauge when a user logs in.
    """
    active_users_gauge.inc()

def user_logged_out():
    """
    Decrement the active users gauge when a user logs out.
    """
    active_users_gauge.dec()

# Set initial values
active_users_gauge.set(0)