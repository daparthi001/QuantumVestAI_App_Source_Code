#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"  # Update with your region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="quantumvestai-db-init"
IMAGE_TAG=$(git rev-parse --short HEAD)  # Use git commit hash as tag

# Update kubeconfig 
echo "Updating kubeconfig..."
aws eks update-kubeconfig --region ${AWS_REGION} --name quantumvestai-cluster

# Apply job with updated image
echo "Applying database initialization job..."
cat k8s/db-init-job.yaml | \
  sed "s|\${AWS_ACCOUNT_ID}|${AWS_ACCOUNT_ID}|g" | \
  sed "s|\${AWS_REGION}|${AWS_REGION}|g" | \
  sed "s|\${IMAGE_TAG}|${IMAGE_TAG}|g" | \
  kubectl apply -f -

# Wait for job to complete
echo "Waiting for database initialization job to complete..."
kubectl wait --for=condition=complete --timeout=300s job/db-init-job -n quantumvestai

# Show logs
echo "Database initialization job logs:"
POD_NAME=$(kubectl get pods -n quantumvestai -l job-name=db-init-job -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n quantumvestai $POD_NAME

echo "Database initialization completed!"