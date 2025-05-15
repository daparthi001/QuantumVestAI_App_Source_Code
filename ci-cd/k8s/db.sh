#!/bin/bash
# Script to update the RDS credentials secret to separate hostname and port

# Get the secret name
SECRET_NAME="quantumvestai-cluster-rds-credentials"
NAMESPACE="dev"

# Get current values
USERNAME=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.username}' | base64 --decode)
PASSWORD=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.password}' | base64 --decode)
ENDPOINT=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.endpoint}' | base64 --decode)
DATABASE=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.database}' | base64 --decode)
PORT=$(kubectl get secret $SECRET_NAME -n $NAMESPACE -o jsonpath='{.data.port}' | base64 --decode)

# Extract just the hostname part from the endpoint
HOSTNAME=$(echo $ENDPOINT | cut -d':' -f1)

echo "Updating secret with hostname: $HOSTNAME"

# Create a new secret with the correct values
kubectl create secret generic $SECRET_NAME -n $NAMESPACE \
  --from-literal=username="$USERNAME" \
  --from-literal=password="$PASSWORD" \
  --from-literal=endpoint="$HOSTNAME" \
  --from-literal=port="$PORT" \
  --from-literal=database="$DATABASE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Secret updated. The endpoint now contains only the hostname."