#!/bin/bash
# Script to create a ConfigMap with only registration-fix.js
# Created: 2025-08-04
# Author: gayatri

set -e

echo "=== Deleting existing ui-scripts ConfigMap ==="
kubectl delete configmap ui-scripts -n dev --ignore-not-found=true

echo "=== Creating ui-scripts ConfigMap with only registration-fix.js ==="
kubectl create configmap ui-scripts -n dev --from-file=registration-fix.js=/Users/gayatri/QuantumVestAI_App_Source_Code/registration-fix.js

echo "=== Adding labels to ConfigMap ==="
kubectl label configmap ui-scripts -n dev app=quantumvestai environment=development tier=frontend --overwrite

echo "=== Describing ConfigMap content ==="
kubectl describe configmap ui-scripts -n dev
