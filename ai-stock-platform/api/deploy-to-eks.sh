#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"  # Update with your region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="quantumvestai-api"
IMAGE_TAG=$(git rev-parse --short HEAD)  # Use git commit hash as tag

# Build and push Docker image
echo "Building Docker image..."
docker build -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG} .
docker tag ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG} \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

echo "Pushing image to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Update kube config
echo "Updating kubeconfig..."
aws eks update-kubeconfig --region ${AWS_REGION} --name quantumvestai-cluster

# Deploy to Kubernetes
echo "Deploying to EKS..."

# Create namespace if it doesn't exist
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/service-account.yaml
kubectl apply -f k8s/storage.yaml
kubectl apply -f k8s/service.yaml

# Update deployment with new image tag
export AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}
export AWS_REGION=${AWS_REGION}
export IMAGE_TAG=${IMAGE_TAG}
envsubst < k8s/deployment.yaml | kubectl apply -f -

# Apply ingress and HPA
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

echo "Deployment complete. Watching rollout..."
kubectl rollout status deployment/quantumvestai-api -n quantumvestai

echo "API is now deployed on EKS!"