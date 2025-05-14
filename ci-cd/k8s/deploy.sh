#!/bin/bash
set -e
set -o pipefail

# This script deploys the QuantumVestAI application to a Kubernetes cluster
echo "QuantumVestAI Kubernetes Deployment"
echo "=================================="

# Verify required tools
echo "Checking required tools..."
for cmd in kubectl git sed; do
  if ! command -v $cmd &> /dev/null; then
    echo "Error: $cmd is not installed or not in PATH"
    exit 1
  fi
done

# Verify Kubernetes context
CURRENT_CONTEXT=$(kubectl config current-context)
echo "Current Kubernetes context: $CURRENT_CONTEXT"
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Deployment cancelled"
  exit 0
fi

# Set your Docker registry and other variables
DOCKER_REGISTRY="921930869047.dkr.ecr.us-east-1.amazonaws.com/quantumvestai"
IMAGE_TAG=$(git rev-parse --short HEAD)  # Use git commit hash as tag
NAMESPACE="dev"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="${SCRIPT_DIR}/kubernetes"

echo "Deploying QuantumVestAI with:"
echo "- Docker Registry: $DOCKER_REGISTRY"
echo "- Image Tag: $IMAGE_TAG"
echo "- Namespace: $NAMESPACE"
echo "- Kubernetes Directory: $K8S_DIR"

# Check if namespace exists, create if it doesn't
if ! kubectl get namespace $NAMESPACE > /dev/null 2>&1; then
  echo "Creating namespace $NAMESPACE"
  kubectl create namespace $NAMESPACE
else
  echo "Using existing namespace $NAMESPACE"
fi

# Apply ConfigMap first
echo "Applying ConfigMap..."
kubectl apply -f "${K8S_DIR}/configmap.yaml" -n $NAMESPACE

# Apply Secrets
echo "Applying Secrets..."
kubectl apply -f "${K8S_DIR}/secrets.yaml" -n $NAMESPACE

# Apply StorageClass if not using default
if [ -f "${K8S_DIR}/storageclass.yaml" ]; then
  echo "Applying StorageClass..."
  kubectl apply -f "${K8S_DIR}/storageclass.yaml"
fi

# Apply PVC and wait for it to be created
echo "Applying PersistentVolumeClaim..."
kubectl apply -f "${K8S_DIR}/pvc.yaml" -n $NAMESPACE
echo "Waiting for PVC to be created..."
kubectl wait --for=condition=PersistentVolumeClaimBound pvc/quantumvestai-pvc -n $NAMESPACE --timeout=60s || echo "PVC not yet bound, continuing anyway"

# Replace Docker registry and image tag placeholders
echo "Preparing deployment files..."
cp "${K8S_DIR}/deployment.yaml" "${K8S_DIR}/deployment.yaml.bak"
cp "${K8S_DIR}/cronjob.yaml" "${K8S_DIR}/cronjob.yaml.bak"
sed -e "s|\${DOCKER_REGISTRY}|$DOCKER_REGISTRY|g" -e "s|\${IMAGE_TAG}|$IMAGE_TAG|g" "${K8S_DIR}/deployment.yaml" > "${K8S_DIR}/deployment-updated.yaml"
sed -e "s|\${DOCKER_REGISTRY}|$DOCKER_REGISTRY|g" -e "s|\${IMAGE_TAG}|$IMAGE_TAG|g" "${K8S_DIR}/cronjob.yaml" > "${K8S_DIR}/cronjob-updated.yaml"

# Apply Deployment, Service, and Ingress
echo "Applying Deployment..."
kubectl apply -f "${K8S_DIR}/deployment-updated.yaml" -n $NAMESPACE

# Wait for deployment to be ready (with timeout)
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/quantumvestai -n $NAMESPACE --timeout=300s || {
  echo "Deployment did not complete in time, check logs for details"
  kubectl get pods -n $NAMESPACE -l app=quantumvestai
  kubectl describe pods -n $NAMESPACE -l app=quantumvestai
}

# Apply HPA
echo "Applying HorizontalPodAutoscaler..."
kubectl apply -f "${K8S_DIR}/hpa.yaml" -n $NAMESPACE

# Apply ResourceQuota
echo "Applying ResourceQuota..."
kubectl apply -f "${K8S_DIR}/resourcequota.yaml" -n $NAMESPACE

# Apply CronJob
echo "Applying CronJob..."
kubectl apply -f "${K8S_DIR}/cronjob-updated.yaml" -n $NAMESPACE

# Apply ServiceMonitor if Prometheus is installed
if kubectl get crd servicemonitors.monitoring.coreos.com > /dev/null 2>&1; then
  echo "Applying ServiceMonitor..."
  kubectl apply -f "${K8S_DIR}/servicemonitor.yaml" -n $NAMESPACE
else
  echo "Skipping ServiceMonitor as Prometheus CRDs are not installed"
fi

# Restore original files
mv "${K8S_DIR}/deployment.yaml.bak" "${K8S_DIR}/deployment.yaml"
mv "${K8S_DIR}/cronjob.yaml.bak" "${K8S_DIR}/cronjob.yaml"

# Clean up temporary files
rm -f "${K8S_DIR}/deployment-updated.yaml" "${K8S_DIR}/cronjob-updated.yaml"

# Check all deployed resources
echo "Deployment complete. Summary of deployed resources:"
echo "------------------------------------------------"
echo "Pods:"
kubectl get pods -n $NAMESPACE -l app=quantumvestai -o wide
echo
echo "Services:"
kubectl get svc -n $NAMESPACE -l app=quantumvestai
echo
echo "Ingress:"
kubectl get ingress -n $NAMESPACE
echo
echo "PersistentVolumeClaims:"
kubectl get pvc -n $NAMESPACE
echo
echo "HorizontalPodAutoscaler:"
kubectl get hpa -n $NAMESPACE
echo
echo "CronJobs:"
kubectl get cronjobs -n $NAMESPACE

# Provide useful commands for monitoring
echo
echo "Useful commands:"
echo "  View logs: kubectl logs -f -l app=quantumvestai -n $NAMESPACE"
echo "  Shell into pod: kubectl exec -it \$(kubectl get pod -l app=quantumvestai -n $NAMESPACE -o jsonpath='{.items[0].metadata.name}') -n $NAMESPACE -- /bin/bash"
echo "  Port forward to service: kubectl port-forward svc/quantumvestai -n $NAMESPACE 8080:80"

echo
echo "Deployment script completed successfully!"