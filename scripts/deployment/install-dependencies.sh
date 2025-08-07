#!/bin/bash
# QuantumVestAI UI Dependencies Installation Script
# Created: 2025-08-04
# Author: gayatri

set -e

echo "=== QuantumVestAI: Installing missing dependencies ==="

# Check if running in Node.js environment
if command -v npm &> /dev/null; then
    echo "Installing missing NPM packages..."
    # Install essential packages if they're missing
    npm list react || npm install --no-save react
    npm list react-dom || npm install --no-save react-dom
    npm list axios || npm install --no-save axios
    npm list chart.js || npm install --no-save chart.js
    npm list react-chartjs-2 || npm install --no-save react-chartjs-2
    npm list @tanstack/react-query || npm install --no-save @tanstack/react-query
    echo "NPM packages check completed"
fi

# Check if running in Python environment
if command -v pip &> /dev/null; then
    echo "Installing missing Python packages..."
    # Install essential packages if they're missing
    pip list | grep -i fastapi || pip install --no-cache-dir fastapi
    pip list | grep -i uvicorn || pip install --no-cache-dir uvicorn
    pip list | grep -i aiohttp || pip install --no-cache-dir aiohttp
    pip list | grep -i requests || pip install --no-cache-dir requests
    pip list | grep -i jinja2 || pip install --no-cache-dir jinja2
    echo "Python packages check completed"
fi

echo "=== Dependencies installation complete ==="
