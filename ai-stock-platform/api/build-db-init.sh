#!/bin/bash
# DB Initialization Docker Image Build Script
# Created: 2025-05-15 20:23:18
# Author: daparthi001

set -e

# Set variables
export ECR_REPOSITORY="quantumvestai"
export IMAGE_TAG="latest"
export AWS_REGION="us-east-1"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "012345678901")
export ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Ensure the Dockerfile.db-init exists
if [ ! -f "Dockerfile.db-init" ]; then
  echo "Error: Dockerfile.db-init not found."
  exit 1
fi

# Set Python path for Alembic and all migration commands
export PYTHONPATH="$(pwd)/ai-stock-platform:$(pwd):/app/core:$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"

# Show current directory contents
echo "Current directory contents:"
ls -la

echo "Building database initialization Docker image..."
docker build -t ${ECR_URI}/${ECR_REPOSITORY}:db-init-${IMAGE_TAG} -f Dockerfile.db-init .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Image: ${ECR_URI}/${ECR_REPOSITORY}:db-init-${IMAGE_TAG}"
    
    # Optionally push to ECR
    read -p "Push to ECR? (y/n): " push_to_ecr
    if [ "$push_to_ecr" == "y" ]; then
        aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}
        docker push ${ECR_URI}/${ECR_REPOSITORY}:db-init-${IMAGE_TAG}
    fi
else
    echo "Build failed!"
fi