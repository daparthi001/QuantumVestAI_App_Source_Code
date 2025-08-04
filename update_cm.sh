#!/bin/bash
# Simple script to update the ui-scripts ConfigMap

set -x  # Enable command tracing

echo "=== Deleting existing ui-scripts ConfigMap ==="
kubectl delete configmap ui-scripts -n dev --ignore-not-found

echo "=== Creating ui-scripts ConfigMap with all files ==="
kubectl create configmap ui-scripts -n dev \
  --from-file=registration-fix.js=/Users/gayatri/QuantumVestAI_App_Source_Code/registration-fix.js \
  --from-file=fix-imports.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/fix-imports.sh \
  --from-file=install-dependencies.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/install-dependencies.sh \
  --from-file=startup-wrapper.sh=/Users/gayatri/QuantumVestAI_App_Source_Code/startup-wrapper.sh

echo "=== Adding labels to ConfigMap ==="
kubectl label configmap ui-scripts -n dev \
  app=quantumvestai \
  environment=development \
  tier=frontend

echo "=== Checking ConfigMap content ==="
kubectl get configmap ui-scripts -n dev -o jsonpath='{.data}' | jq
