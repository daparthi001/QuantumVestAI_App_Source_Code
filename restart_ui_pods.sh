#!/bin/bash
# Script to restart UI pods to pick up ConfigMap changes
# Created: 2025-08-04

set -e

echo "=== Restarting QuantumVestAI UI pods ==="

# First, list all pods to see what's available
echo "Available pods in dev namespace:"
kubectl get pods -n dev

# Get all UI pods - trying various label combinations
echo "Looking for UI pods..."
echo "Searching for pods with name containing 'ui'..."
UI_PODS=$(kubectl get pods -n dev -o name | grep -i -E 'ui')

if [ -z "$UI_PODS" ]; then
  echo "No pods with 'ui' in name. Looking for pods with 'frontend' in name..."
  UI_PODS=$(kubectl get pods -n dev -o name | grep -i -E 'frontend')
fi

if [ -z "$UI_PODS" ]; then
  echo "No UI-related pods found automatically. Please select a pod manually:"
  kubectl get pods -n dev
  read -p "Enter the name of the UI pod (without the 'pod/' prefix): " POD_NAME
  UI_PODS="pod/$POD_NAME"
fi

echo "Found UI pods: $UI_PODS"

# Verify the pods actually exist (in case they were restarted/replaced)
VERIFIED_PODS=""
for POD in $UI_PODS; do
  if kubectl get $POD -n dev &> /dev/null; then
    echo "$POD exists and will be processed"
    VERIFIED_PODS="$VERIFIED_PODS $POD"
  else
    echo "$POD not found, might have been restarted/replaced"
  fi
done

if [ -z "$VERIFIED_PODS" ]; then
  echo "No verified UI pods found. Getting latest pod list..."
  kubectl get pods -n dev
  read -p "Enter the name of the UI pod (without the 'pod/' prefix): " POD_NAME
  VERIFIED_PODS="pod/$POD_NAME"
fi

UI_PODS=$VERIFIED_PODS

# Restart pods one by one
for POD in $UI_PODS; do
  echo "Restarting $POD..."
  kubectl delete $POD -n dev
  echo "Waiting for new pod to be ready..."
  sleep 3
done

# Wait for all pods to be ready
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pods -l app=quantumvestai,tier=frontend -n dev --timeout=120s

echo "=== UI pods restarted ==="

# Verify pods have the ConfigMap mounted
echo "=== Verifying ConfigMap mount ==="
for POD in $(kubectl get pods -n dev -l app=quantumvestai,tier=frontend -o name); do
  echo "Checking $POD..."
  kubectl describe $POD -n dev | grep -A 5 "ui-scripts"
done

echo "=== Pod restart complete ==="
