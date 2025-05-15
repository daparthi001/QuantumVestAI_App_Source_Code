#!/bin/bash

# Script to deploy QuantumVestAI UI to Kubernetes on AWS EKS
# Usage: ./deploy-aws.sh [environment] [version]

set -e

# Default values
ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
NAMESPACE="quantumvestai"
AWS_REGION="us-west-2" # Change to your AWS region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/quantumvestai-ui"
IMAGE_TAG=${VERSION}

# Display deployment info
echo "Deploying QuantumVestAI UI on AWS EKS"
echo "Environment: ${ENVIRONMENT}"
echo "Version: ${VERSION}"
echo "ECR Repository: ${ECR_REPOSITORY}"
echo "Namespace: ${NAMESPACE}"

# Login to ECR
echo "Logging in to AWS ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Replace variables in deployment files
echo "Preparing deployment files..."
sed -i "s|image: \${DOCKER_REGISTRY}/quantumvestai-ui:\${IMAGE_TAG}|image: ${ECR_REPOSITORY}:${IMAGE_TAG}|g" k8s/deployment.yaml
sed -i "s|--cluster-name=your-eks-cluster|--cluster-name=${EKS_CLUSTER_NAME}|g" k8s/aws-load-balancer-controller.yaml
sed -i "s|arn:aws:acm:region:account-id:certificate/certificate-id|${SSL_CERT_ARN}|g" k8s/ingress.yaml

# Apply AWS-specific configurations first
echo "Applying AWS Load Balancer Controller..."
kubectl apply -f k8s/aws-load-balancer-controller.yaml

# Wait for the controller to be ready
echo "Waiting for AWS Load Balancer Controller to be ready..."
kubectl rollout status deployment/aws-load-balancer-controller -n kube-system

# Apply Kubernetes configurations
echo "Applying Kubernetes configuration files..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/service-account.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/api-ingress.yaml  # Apply the API ingress
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/redis-pvc.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml
kubectl apply -f k8s/network-policy.yaml
kubectl apply -f k8s/resource-quota.yaml

echo "Deployment complete!"

# Wait for rollout to complete
kubectl rollout status deployment/quantumvestai-ui -n ${NAMESPACE}

echo "QuantumVestAI UI deployment successful!"
echo "ALB Ingress may take a few minutes to provision the load balancer..."

# Get the ALB DNS name after it's created
echo "Waiting for ALB to be provisioned..."
sleep 30
ALB_DNS=$(kubectl get ingress quantumvestai-ui-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

if [ -n "$ALB_DNS" ]; then
  echo "Application is accessible at: https://${ALB_DNS}"
  echo "Once DNS propagation is complete, the application will be available at: https://app.quantumvestai.com"
else
  echo "ALB is still being provisioned. Check status with:"
  echo "kubectl get ingress quantumvestai-ui-ingress -n ${NAMESPACE}"
fi