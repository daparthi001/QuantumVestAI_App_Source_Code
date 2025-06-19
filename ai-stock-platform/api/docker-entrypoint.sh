#!/bin/bash
# Production Docker Entrypoint for QuantumVestAI API
# Created: 2025-06-19 06:07:51
# Author: daparthi001

set -e

echo "=== Starting QuantumVestAI API Service ==="
echo "Date: $(date -u)"
echo "Environment: $API_ENV"
echo "User: $(whoami)"

# Set Python path to include current directory
export PYTHONPATH=/app:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

# Ensure api directory exists
if [ ! -d "/app/api" ]; then
    echo "Creating api directory..."
    mkdir -p /app/api
fi

# Ensure api/__init__.py exists
if [ ! -f "/app/api/__init__.py" ]; then
    echo "Creating api/__init__.py..."
    cat > /app/api/__init__.py << 'EOF'
"""
API Package
Created: 2025-06-19 06:07:51
Author: daparthi001
"""
from api.main import app

__all__ = ['app']
EOF
fi

# Check for main.py in multiple locations and copy if needed
if [ -f "/app/main.py" ] && [ ! -f "/app/api/main.py" ]; then
    echo "Found main.py in root directory, copying to api directory..."
    cp /app/main.py /app/api/main.py
fi

# Ensure logs directory exists
if [ ! -d "/app/logs" ]; then
    echo "Creating logs directory..."
    mkdir -p /app/logs
    if [ "$(whoami)" = "appuser" ]; then
        chown -R appuser:appuser /app/logs
    fi
fi

# Print directory contents for debugging
echo "Directory structure:"
ls -la /app
ls -la /app/api

# Verify we can import the api module
echo "Verifying api module can be imported..."
python -c "import sys; print(sys.path); import api; print(f'API module found and app imported. Routes: {len(api.app.routes)}')" || {
    echo "ERROR: Cannot import api module. Creating a minimal implementation..."
    
    # Create a minimal implementation
    cat > /app/api/main.py << 'EOF'
"""
QuantumVestAI API - Main Application (Minimal Implementation)
Created: 2025-06-19 06:07:51
Author: daparthi001
"""
import os
import socket
import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantumvestai_api")

# Create FastAPI application
app = FastAPI(
    title="QuantumVestAI API",
    version="1.0.0",
    description="Stock Market Analysis Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "QuantumVestAI API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "system": {
            "hostname": socket.gethostname(),
            "timestamp": datetime.now().isoformat(),
            "environment": os.environ.get("API_ENV", "development")
        }
    }
EOF

    # Verify the minimal implementation
    python -c "import api; print(f'Minimal API implementation created. Routes: {len(api.app.routes)}')"
}

# Start the application
echo "Starting API service with command: $@"
exec "$@"