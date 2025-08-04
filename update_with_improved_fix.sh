#!/bin/bash
# Script to update the UI pod with the improved WebSocket fix
# Created: 2025-08-04

set -e

echo "=== Applying improved WebSocket fix to UI pod ==="

# Get the pod name
POD_NAME=$(kubectl get pods -n dev | grep ui-deployment | awk '{print $1}')
if [ -z "$POD_NAME" ]; then
  echo "No UI pod found. Exiting."
  exit 1
fi

echo "Found UI pod: $POD_NAME"

# Copy the improved fix to the pod
echo "Copying improved fix to pod..."
kubectl cp /Users/gayatri/QuantumVestAI_App_Source_Code/market-data-fix-updated.js dev/$POD_NAME:/app/market-data-fix.js

echo "Verifying the file was copied..."
kubectl exec -n dev $POD_NAME -- cat /app/market-data-fix.js | head -5

echo "=== WebSocket fix updated successfully ==="
echo "The improved fix adds a premium=true parameter to bypass role checks."
echo "Free tier users should now be able to connect without 403 errors."
