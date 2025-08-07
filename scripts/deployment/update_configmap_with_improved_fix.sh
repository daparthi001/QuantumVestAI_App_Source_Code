#!/bin/bash
# Script to update ConfigMap with improved WebSocket fix
# Created: 2025-08-04
# Author: GitHub Copilot

set -e

echo "=== Updating ConfigMap with improved WebSocket fix ==="

# Create a temporary directory to store the files
TMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TMP_DIR"

# Copy the updated market-data-fix.js to the temporary directory
cp /Users/gayatri/QuantumVestAI_App_Source_Code/market-data-fix-updated.js $TMP_DIR/market-data-fix.js
echo "Copied updated WebSocket fix script to temporary directory"

# Extract existing files from ConfigMap to preserve them
echo "Extracting existing files from ConfigMap"
kubectl get configmap ui-scripts -n dev -o jsonpath='{.data.registration-fix\.js}' > $TMP_DIR/registration-fix.js
kubectl get configmap ui-scripts -n dev -o jsonpath='{.data.fix-imports\.sh}' > $TMP_DIR/fix-imports.sh
kubectl get configmap ui-scripts -n dev -o jsonpath='{.data.install-dependencies\.sh}' > $TMP_DIR/install-dependencies.sh
kubectl get configmap ui-scripts -n dev -o jsonpath='{.data.startup-wrapper\.sh}' > $TMP_DIR/startup-wrapper.sh

# Delete the existing ConfigMap
echo "Deleting existing ConfigMap"
kubectl delete configmap ui-scripts -n dev --ignore-not-found=true

# Create the new ConfigMap with the updated files
echo "Creating new ConfigMap with updated WebSocket fix"
kubectl create configmap ui-scripts -n dev \
  --from-file=registration-fix.js=$TMP_DIR/registration-fix.js \
  --from-file=market-data-fix.js=$TMP_DIR/market-data-fix.js \
  --from-file=fix-imports.sh=$TMP_DIR/fix-imports.sh \
  --from-file=install-dependencies.sh=$TMP_DIR/install-dependencies.sh \
  --from-file=startup-wrapper.sh=$TMP_DIR/startup-wrapper.sh

# Add labels to the ConfigMap
echo "Adding labels to ConfigMap"
kubectl label configmap ui-scripts -n dev app=quantumvestai environment=development tier=frontend --overwrite

# Clean up temporary directory
echo "Cleaning up temporary directory"
rm -rf $TMP_DIR

echo "=== ConfigMap updated successfully ==="
echo "The improved WebSocket fix has been added to the ConfigMap"
