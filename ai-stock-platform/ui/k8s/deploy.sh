#!/bin/bash

# Script to deploy QuantumVestAI UI to Kubernetes
# Usage: ./deploy.sh [environment] [version]

set -e

# Default values
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
NAMESPACE="quantumvestai"
DOCKER_REGISTRY="your-registry.io"
IMAGE_TAG=${VERSION}

# Display deployment info
echo "Deploying QuantumVestAI UI"
echo "Environment: ${ENVIRONMENT}"
echo "Version: ${VERSION}"
echo "Namespace: ${NAMESPACE}"

# Replace variables in deployment file
sed -i "s|\${DOCKER_REGISTRY}|${DOCKER_REGISTRY}|g" k8s/deployment.yaml
sed -i "s|\${IMAGE_TAG}|${IMAGE_TAG}|g" k8s/deployment.yaml

# Apply Kubernetes configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/service-account.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/redis-pvc.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/resource-quota.yaml

echo "Deployment complete!"

# Wait for rollout to complete
kubectl rollout status deployment/quantumvestai-ui -n ${NAMESPACE}

echo "QuantumVestAI UI deployment successful"