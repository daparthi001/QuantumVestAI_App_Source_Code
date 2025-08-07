#!/bin/bash

# QuantumVestAI WebSocket Permission Fix Deployment Script
# Created: 2025-08-07
# Author: GitHub Copilot

set -e  # Exit on error

echo "===== QuantumVestAI WebSocket Permission Fix Deployment ====="
echo "Starting deployment at $(date)"

# Set the project directory
PROJECT_DIR="/Users/gayatri/QuantumVestAI_App_Source_Code"
API_DIR="${PROJECT_DIR}/ai-stock-platform/api"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "ERROR: Project directory not found: $PROJECT_DIR"
    exit 1
fi

# 1. Create backup of original files
echo "Creating backups..."
mkdir -p "${PROJECT_DIR}/backups/$(date +%Y-%m-%d)"
cp -f "${API_DIR}/routers/websocket.py" "${PROJECT_DIR}/backups/$(date +%Y-%m-%d)/"
echo "Backups created successfully."

# 2. Run the WebSocket fix script
echo "Running WebSocket fix script..."
cd "$PROJECT_DIR"
python websocket-role-fix.py
if [ $? -ne 0 ]; then
    echo "ERROR: WebSocket fix script failed!"
    exit 1
fi
echo "WebSocket fix script completed successfully."

# 3. Run tests
echo "Running WebSocket permission tests..."
cd "$API_DIR"
python -m pytest tests/test_websocket_permissions.py -v
if [ $? -ne 0 ]; then
    echo "ERROR: WebSocket permission tests failed!"
    exit 1
fi
echo "WebSocket permission tests passed successfully."

# 4. Restart API service (if in production environment)
if [ -n "$KUBECONFIG" ]; then
    echo "Restarting API service in Kubernetes..."
    kubectl rollout restart deployment quantumvestai-dev-api
    echo "Waiting for deployment to complete..."
    kubectl rollout status deployment quantumvestai-dev-api --timeout=120s
    if [ $? -ne 0 ]; then
        echo "WARNING: Deployment may not have completed successfully."
    else
        echo "API service restarted successfully."
    fi
else
    echo "Not in Kubernetes environment. Manual API service restart may be required."
    echo "Run the following command to restart the API service:"
    echo "kubectl rollout restart deployment quantumvestai-dev-api"
fi

# 5. Verify the deployment
echo "Verifying WebSocket permissions..."
cd "$PROJECT_DIR"
python -c "
import requests
import json

# Create a free tier user token for testing
test_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXIiLCJyb2xlIjoiZnJlZSJ9.abc123placeholder'

# Test the market-data endpoint
print('Testing /market-data endpoint...')
response = requests.get('https://api-dev.quantumvestai.com/api/v1/market-data/ping', 
                       headers={'Authorization': f'Bearer {test_token}'})
print(f'Status code: {response.status_code}')
print(f'Response: {response.text}')

# Note: Full WebSocket testing requires a WebSocket client
print('\\nFor complete verification, please run the WebSocket client test script:')
print('python test_websocket_client.py')
"

echo "===== Deployment completed at $(date) ====="
echo "Note: Verify the WebSocket connections in the production environment."
