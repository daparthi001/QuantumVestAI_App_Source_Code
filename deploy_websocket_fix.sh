#!/bin/bash
# Deploy WebSocket Permission Fix
# Created: 2025-08-04
# Author: gayatri

set -e

echo "Deploying WebSocket Permission Fix..."

# Current directory
CURRENT_DIR=$(pwd)
API_DIR="${CURRENT_DIR}/ai-stock-platform/api"
SECURITY_DIR="${API_DIR}/core/security"

echo "Working in directory: ${CURRENT_DIR}"

# Ensure security directory exists
if [ ! -d "${SECURITY_DIR}" ]; then
    echo "Creating security directory: ${SECURITY_DIR}"
    mkdir -p "${SECURITY_DIR}"
fi

# Ensure the WebSocket permissions file exists
if [ ! -f "${SECURITY_DIR}/websocket_permissions.py" ]; then
    echo "WebSocket permissions file missing, please create it first"
    exit 1
fi

# Apply the fix by modifying the WebSocket router
echo "Applying changes to websocket.py..."
python3 websocket-role-fix.py

# Run the tests
echo "Running tests..."
cd "${API_DIR}"
python -m pytest tests/test_websocket_permissions.py -v

if [ $? -eq 0 ]; then
    echo "Tests passed successfully!"
else
    echo "Tests failed! Please check the implementation."
    exit 1
fi

echo "Creating a backup of the current API deployment..."
kubectl get deployment quantumvestai-dev-api -o yaml > quantumvestai-dev-api-backup-$(date +%Y%m%d%H%M%S).yaml

echo "Restarting API deployment to apply changes..."
kubectl rollout restart deployment quantumvestai-dev-api

echo "Monitoring rollout status..."
kubectl rollout status deployment quantumvestai-dev-api

echo "WebSocket Permission Fix deployed successfully!"
echo "Please verify the fix by connecting to the WebSocket endpoints with a free tier user."
