#!/bin/bash
# Script to create the ui-scripts ConfigMap with correct formatting
# Created: 2025-08-04
# Author: gayatri

set -e

echo "=== Creating ui-scripts ConfigMap with properly formatted content ==="

# First delete any existing ConfigMap
kubectl delete configmap ui-scripts -n dev --ignore-not-found=true

# Create the ConfigMap with all files properly formatted
kubectl create configmap ui-scripts -n dev \
  --from-file=registration-fix.js=/Users/gayatri/QuantumVestAI_App_Source_Code/registration-fix.js \
  --from-file=market-data-fix.js=/Users/gayatri/QuantumVestAI_App_Source_Code/market-data-fix.js \
  --from-file=fix-imports.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/fix-imports.sh \
  --from-file=install-dependencies.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/install-dependencies.sh \
  --from-file=startup-wrapper.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/startup-wrapper.sh

# Add labels to the ConfigMap
kubectl label configmap ui-scripts -n dev app=quantumvestai environment=development tier=frontend --overwrite

echo "=== Verifying ConfigMap content ==="
kubectl get configmap ui-scripts -n dev -o yaml

echo "=== ConfigMap creation completed ==="
