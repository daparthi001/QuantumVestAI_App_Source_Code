#!/bin/bash
# Database Connection Testing Script
# Created: 2025-05-20 07:58:24
# Author: daparthi001

set -e

echo "=== Starting Database Connection Tests at $(date -u) ==="
echo "Timestamp: 2025-05-20 07:58:24"
echo "Tester: daparthi001"

NAMESPACE="dev"
RDS_HOST="quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com"
INTERNAL_HOST="172.20.234.34"
PORT="5432"

# Function to test TCP connectivity
test_tcp() {
    local host=$1
    local port=$2
    echo "Testing TCP connectivity to $host:$port..."
    if nc -zv -w 5 "$host" "$port" 2>&1; then
        echo "✅ TCP connection successful"
        return 0
    else
        echo "❌ TCP connection failed"
        return 1
    fi
}

# Create verification job
echo "Creating verification job..."
kubectl apply -f ci-cd/k8s/dev/verify-db-connections-job.yaml

# Wait for job pod
echo "Waiting for job pod to start..."
sleep 5

# Get pod name
POD_NAME=$(kubectl get pods -n $NAMESPACE -l component=connection-verify -o jsonpath='{.items[0].metadata.name}')

# Print pod details
echo ""
echo "=== Pod Details ==="
kubectl get pod $POD_NAME -n $NAMESPACE -o wide

# Stream logs
echo ""
echo "=== Streaming Job Logs ==="
kubectl logs -f $POD_NAME -n $NAMESPACE &
LOGS_PID=$!

# Wait for job completion
echo ""
echo "Waiting for verification job to complete..."
if kubectl wait --for=condition=complete job/verify-db-connections -n $NAMESPACE --timeout=60s; then
    kill $LOGS_PID 2>/dev/null
    echo "✅ Verification job completed successfully!"
else
    kill $LOGS_PID 2>/dev/null
    echo "❌ Verification job failed!"
    echo ""
    echo "=== Debug Information ==="
    echo "1. Testing direct TCP connectivity..."
    test_tcp "$RDS_HOST" "$PORT"
    test_tcp "$INTERNAL_HOST" "$PORT"
    
    echo ""
    echo "2. Checking pod description..."
    kubectl describe pod $POD_NAME -n $NAMESPACE
    
    echo ""
    echo "3. Checking pod logs..."
    kubectl logs $POD_NAME -n $NAMESPACE
    
    exit 1
fi

# Cleanup
echo ""
echo "Cleaning up verification job..."
kubectl delete job verify-db-connections -n $NAMESPACE

echo ""
echo "=== Verification completed at $(date -u) ==="