#!/bin/bash
# Quick Fix for WebSocket Authentication Error
# Created: 2025-08-04
# Author: gayatri

set -e

echo "Applying API_PREFIX quick fix to running pods..."

# Get pod names
API_PODS=$(kubectl get pods -n quantumvestai -l app=quantumvestai-api -o name)

if [ -z "$API_PODS" ]; then
  echo "No API pods found in the quantumvestai namespace"
  exit 1
fi

for POD in $API_PODS; do
  echo "Applying fix to $POD..."
  
  # Create a quick fix script to update the authentication.py file
  kubectl exec $POD -n quantumvestai -- bash -c '
    if [ -f /app/core/security/authentication.py ]; then
      # Make a backup
      cp /app/core/security/authentication.py /app/core/security/authentication.py.bak
      
      # Replace API_PREFIX with API_V1_STR
      sed -i "s/settings.API_PREFIX/settings.API_V1_STR/g" /app/core/security/authentication.py
      
      echo "Fix applied to authentication.py"
    else
      echo "Could not find authentication.py file"
    fi
  '
done

echo "Fix applied to all pods. Restarting deployment..."
kubectl rollout restart deployment/quantumvestai-api -n quantumvestai

echo "Waiting for restart to complete..."
kubectl rollout status deployment/quantumvestai-api -n quantumvestai

echo "Fix applied successfully!"
