#!/bin/bash
# RDS Connection Verification Script
# Created: 2025-05-20 07:51:26
# Author: daparthi001

set -e

echo "=== Starting RDS connection verification at $(date -u) ==="
NAMESPACE="dev"
SECRET_NAME="quantumvestai-cluster-rds-credentials"

# Function to decode base64 secret
decode_secret() {
    local secret_name=$1
    local key=$2
    kubectl get secret $secret_name -n $NAMESPACE -o jsonpath="{.data.$key}" | base64 --decode
}

# Check if secret exists
if ! kubectl get secret $SECRET_NAME -n $NAMESPACE >/dev/null 2>&1; then
    echo "❌ Error: Secret '$SECRET_NAME' not found in namespace '$NAMESPACE'!"
    exit 1
fi

echo "✅ Found secret: $SECRET_NAME"

# Verify all required keys exist
REQUIRED_KEYS=("host" "port" "username" "password" "dbname")
echo "Checking required secret keys..."
for key in "${REQUIRED_KEYS[@]}"; do
    if ! kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath="{.data.$key}" >/dev/null 2>&1; then
        echo "❌ Error: Key '$key' not found in secret!"
        exit 1
    fi
    echo "✅ Found key: $key"
done

echo "=== Secret Details ==="
echo "Host: $(decode_secret $SECRET_NAME host)"
echo "Port: $(decode_secret $SECRET_NAME port)"
echo "Database: $(decode_secret $SECRET_NAME dbname)"
echo "Username: $(decode_secret $SECRET_NAME username)"
echo "=== End Secret Details ==="

# Create verification job
echo "Creating verification job..."
kubectl apply -f ci-cd/k8s/dev/verify-rds-secrets-job.yaml

# Wait for job completion
echo "Waiting for verification job to complete..."
if kubectl wait --for=condition=complete job/verify-rds-secrets -n $NAMESPACE --timeout=60s; then
    echo "✅ Verification job completed successfully!"
    echo "=== Job Logs ==="
    kubectl logs job/verify-rds-secrets -n $NAMESPACE
    echo "=== End Job Logs ==="
else
    echo "❌ Verification job failed!"
    echo "=== Error Logs ==="
    kubectl logs job/verify-rds-secrets -n $NAMESPACE
    echo "=== End Error Logs ==="
    
    echo "=== Debug Information ==="
    echo "1. Checking pod status..."
    kubectl get pods -n $NAMESPACE -l job-name=verify-rds-secrets
    
    echo "2. Checking pod description..."
    kubectl describe pods -n $NAMESPACE -l job-name=verify-rds-secrets
    
    echo "3. Checking job description..."
    kubectl describe job verify-rds-secrets -n $NAMESPACE
    echo "=== End Debug Information ==="
    
    exit 1
fi

# Cleanup
echo "Cleaning up verification job..."
kubectl delete job verify-rds-secrets -n $NAMESPACE

echo "=== Verification completed at $(date -u) ==="