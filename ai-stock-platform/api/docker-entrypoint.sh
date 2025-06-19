#!/bin/bash
# Docker Entrypoint Script for QuantumVestAI API
# Updated: 2025-06-19 05:51:42
# Author: daparthi001

set -e

echo "=== Starting QuantumVestAI API Service ==="
echo "Date: $(date)"
echo "Environment: $API_ENV"
echo "User: $(whoami)"
echo "Python: $(python --version)"

# Check for main.py in alternative locations and copy if needed
if [ -f "/app/main.py" ] && [ ! -f "/app/api/main.py" ]; then
    echo "Found main.py in root directory, copying to api directory..."
    cp /app/main.py /app/api/main.py
fi

# Ensure api directory exists
if [ ! -d "/app/api" ]; then
    echo "Creating api directory..."
    mkdir -p /app/api
fi

# Ensure api/__init__.py exists with proper content
if [ ! -f "/app/api/__init__.py" ]; then
    echo "Creating api/__init__.py..."
    cat << 'INITPY' > /app/api/__init__.py
"""
API Package
Created: 2025-05-21 13:57:49
Author: daparthi001
"""
from api.main import app

__all__ = ['app']
INITPY
fi

# Ensure api/main.py exists with at least basic endpoints
if [ ! -f "/app/api/main.py" ]; then
    echo "Creating minimal api/main.py..."
    cat << 'MAINPY' > /app/api/main.py
"""
QuantumVestAI API - Main Application
Created: 2025-06-19 05:51:42
Author: daparthi001
"""
from fastapi import FastAPI
import logging
from datetime import datetime
import os
import socket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantumvestai_api")

app = FastAPI(title="QuantumVestAI API", version="1.0.0")

@app.get("/")
async def root():
    """API root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "name": "QuantumVestAI API",
        "version": "1.0.0",
        "status": "running",
        "environment": os.environ.get("API_ENV", "development"),
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}

@app.get("/api/v1/health")
async def api_health_check():
    """API v1 health check endpoint"""
    logger.info("API v1 health check endpoint accessed")
    system_info = {
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
        "environment": os.environ.get("API_ENV", "development"),
    }
    return {
        "status": "healthy",
        "version": "1.0.0",
        "system": system_info
    }
MAINPY
fi

# Ensure logs directory exists
if [ ! -d "/app/logs" ]; then
    echo "Creating logs directory..."
    mkdir -p /app/logs
    if [ "$(whoami)" = "appuser" ]; then
        chown -R appuser:appuser /app/logs
    fi
fi

# Set Python path
export PYTHONPATH="/app:${PYTHONPATH}"
echo "PYTHONPATH: $PYTHONPATH"

# Print system status
echo "System status:"
echo "  Disk space: $(df -h / | awk 'NR==2 {print $5 " used"}')"
echo "  Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"

# Print current directory structure
echo "Directory structure:"
echo "- /app contents:"
ls -la /app | head -n 20
echo "- /app/api contents:"
ls -la /app/api

# Check if we can import the api module
python -c "import api; print(f'API module found and app imported. App routes: {len(api.app.routes)}')" || echo "Warning: Could not import api module"

# Start the application
echo "Starting API service with command: $@"
exec "$@"