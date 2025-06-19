#!/bin/bash
# Docker Entrypoint Script for QuantumVestAI API
# Updated: 2025-06-19 05:44:13
# Author: daparthi001

set -e

echo "=== Starting QuantumVestAI API Service ==="
echo "Date: $(date)"
echo "Environment: $API_ENV"
echo "User: $(whoami)"
echo "Python: $(python --version)"

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
echo "Current directory structure:"
ls -la /app
ls -la /app/api

# Check if we can import the api module
python -c "import api; print(f'API module found and can be imported. App routes: {len(api.app.routes)}')" || echo "Warning: Could not import api module"

# Start the application
echo "Starting API service with command: $@"
exec "$@"