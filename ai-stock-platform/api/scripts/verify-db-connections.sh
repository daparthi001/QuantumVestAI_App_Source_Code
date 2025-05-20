#!/bin/bash
# Database Connections Verification Script
# Created: 2025-05-20 07:54:45
# Author: daparthi001

set -e

echo "=== Starting Database Connection Verification at $(date -u) ==="
echo "Verifier: daparthi001"

NAMESPACE="dev"

# Create and run verification job
echo "Creating verification job..."
kubectl apply -f ci-cd/k8s/dev/verify-db-connections-job.yaml

# Wait for job to start
echo "Waiting for job pod to start..."
sleep 5

# Get pod name
POD_NAME=$(kubectl get pods -n $NAMESPACE -l component=connection-verify -o jsonpath='{.items[0].metadata.name}')

# Print pod details
echo ""
echo "=== Pod Details ==="
kubectl get pod $POD_NAME -n $NAMESPACE -o wide

# Wait for job completion
echo ""
echo "Waiting for verification job to complete..."
if kubectl wait --for=condition=complete job/verify-db-connections -n $NAMESPACE --timeout=60s; then
    echo "✅ Verification job completed successfully!"
    echo ""
    echo "=== Job Logs ==="
    kubectl logs job/verify-db-connections -n $NAMESPACE
    echo "=== End Job Logs ==="
else
    echo "❌ Verification job failed!"
    echo ""
    echo "=== Error Logs ==="
    kubectl logs job/verify-db-connections -n $NAMESPACE
    echo "=== End Error Logs ==="
    
    echo ""
    echo "=== Pod Description ==="
    kubectl describe pod $POD_NAME -n $NAMESPACE
    exit 1
fi

# Cleanup
echo ""
echo "Cleaning up verification job..."
kubectl delete job verify-db-connections -n $NAMESPACE

echo ""
echo "=== Verification completed at $(date -u) ==="