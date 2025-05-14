#!/bin/bash

# This script deploys the QuantumVestAI application to a Kubernetes cluster

# Set your Docker registry and other variables
DOCKER_REGISTRY="921930869047.dkr.ecr.us-east-1.amazonaws.com/quantumvestai"
IMAGE_TAG=$(git rev-parse --short HEAD)  # Use git commit hash as tag
NAMESPACE="dev"

# Check if namespace exists, create if it doesn't
if ! kubectl get namespace $NAMESPACE > /dev/null 2>&1; then
  echo "Creating namespace $NAMESPACE"
  kubectl create namespace $NAMESPACE
fi

# Apply ConfigMap first
echo "Applying ConfigMap..."
kubectl apply -f kubernetes/configmap.yaml -n $NAMESPACE

# Apply Secrets
echo "Applying Secrets..."
kubectl apply -f kubernetes/secrets.yaml -n $NAMESPACE

# Apply PVC
echo "Applying PersistentVolumeClaim..."
kubectl apply -f kubernetes/pvc.yaml -n $NAMESPACE

# Replace Docker registry placeholder in deployment.yaml
echo "Replacing Docker registry placeholder..."
sed "s|\${DOCKER_REGISTRY}|$DOCKER_REGISTRY|g" kubernetes/deployment.yaml > kubernetes/deployment-updated.yaml

# Apply Deployment, Service, and Ingress
echo "Applying Deployment, Service, and Ingress..."
kubectl apply -f kubernetes/deployment-updated.yaml -n $NAMESPACE

# Apply HPA
echo "Applying HorizontalPodAutoscaler..."
kubectl apply -f kubernetes/hpa.yaml -n $NAMESPACE

# Apply ResourceQuota
echo "Applying ResourceQuota..."
kubectl apply -f kubernetes/resourcequota.yaml -n $NAMESPACE

# Apply CronJob
echo "Applying CronJob..."
sed "s|\${DOCKER_REGISTRY}|$DOCKER_REGISTRY|g" kubernetes/cronjob.yaml > kubernetes/cronjob-updated.yaml
kubectl apply -f kubernetes/cronjob-updated.yaml -n $NAMESPACE

# Apply ServiceMonitor if Prometheus is installed
if kubectl get crd servicemonitors.monitoring.coreos.com > /dev/null 2>&1; then
  echo "Applying ServiceMonitor..."
  kubectl apply -f kubernetes/servicemonitor.yaml -n $NAMESPACE
else
  echo "Skipping ServiceMonitor as Prometheus CRDs are not installed"
fi

# Clean up temporary files
rm kubernetes/deployment-updated.yaml kubernetes/cronjob-updated.yaml

echo "Deployment complete. Checking status..."
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

echo "To check the logs, run: kubectl logs -f -l app=quantumvestai -n $NAMESPACE"