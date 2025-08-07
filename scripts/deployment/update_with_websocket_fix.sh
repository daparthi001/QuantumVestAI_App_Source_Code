#!/bin/bash
# Script to update the ui-scripts ConfigMap with both fixes
# Created: 2025-08-04
# Author: gayatri

set -e

echo "=== Deleting existing ui-scripts ConfigMap ==="
kubectl delete configmap ui-scripts -n dev --ignore-not-found=true

echo "=== Creating new ui-scripts ConfigMap ==="
kubectl create configmap ui-scripts -n dev \
  --from-file=registration-fix.js=/Users/gayatri/QuantumVestAI_App_Source_Code/registration-fix.js \
  --from-file=market-data-fix.js=/Users/gayatri/QuantumVestAI_App_Source_Code/market-data-fix.js \
  --from-file=fix-imports.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/fix-imports.sh \
  --from-file=install-dependencies.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/install-dependencies.sh \
  --from-file=startup-wrapper.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/startup-wrapper.sh

echo "=== Adding labels to ConfigMap ==="
kubectl label configmap ui-scripts -n dev app=quantumvestai environment=development tier=frontend --overwrite

echo "=== ConfigMap updated successfully ==="
