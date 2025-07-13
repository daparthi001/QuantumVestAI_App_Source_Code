"""
FastAPI App Structure Checker
Created: 2025-06-19 04:20:11
Author: daparthi001
"""
import inspect
import os
import sys

# Check if we can import the main app
print("Checking app structure...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

try:
    # Try to import the app
    from main import app
    
    print("\nApp info:")
    print(f"App title: {app.title}")
    print(f"App version: {app.version}")
    
    # List all routes
    print("\nRegistered routes:")
    for route in app.routes:
        path = getattr(route, "path", "unknown")
        name = getattr(route, "name", "unknown")
        methods = getattr(route, "methods", ["unknown"])
        print(f"  Path: {path}, Name: {name}, Methods: {methods}")
    
    # Check imported routers
    print("\nIncluded routers:")
    for router in app.routes:
        if hasattr(router, "prefix"):
            print(f"  Prefix: {router.prefix}, Tags: {router.tags}, Routes: {len(router.routes)}")
    
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()

print("\nChecking for route handler errors...")
try:
    # Create mock request to check route registration
    from fastapi import Request
    from starlette.datastructures import URL
    
    mock_request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/v1/health",
            "headers": [],
            "url": URL("/api/v1/health")
        }
    )
    
    # Try to match the route
    route = app.router.match(mock_request.scope)
    print(f"Route match result: {route}")
except Exception as e:
    print(f"Error checking route handler: {e}")
    import traceback
    traceback.print_exc()
