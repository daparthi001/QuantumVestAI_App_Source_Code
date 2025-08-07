#!/bin/bash
# Script to identify UI pods in the Kubernetes cluster
# Created: 2025-08-04
# Author: GitHub Copilot

set -e

echo "=== Identifying UI pods in Kubernetes cluster ==="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "kubectl could not be found. Please install kubectl and try again."
    exit 1
fi

# Check if we can access the Kubernetes cluster
if ! kubectl get nodes &> /dev/null; then
    echo "Could not access Kubernetes cluster. Please check your kubeconfig and try again."
    exit 1
fi

# List all namespaces
echo "Available namespaces:"
kubectl get namespaces

# Default to 'dev' namespace, but allow user to choose another
DEFAULT_NAMESPACE="dev"
read -p "Enter namespace to search for UI pods [$DEFAULT_NAMESPACE]: " NAMESPACE
NAMESPACE=${NAMESPACE:-$DEFAULT_NAMESPACE}

echo "Searching for pods in namespace: $NAMESPACE"

# Get all pods in the namespace
echo "All pods in $NAMESPACE namespace:"
kubectl get pods -n $NAMESPACE

# Look for UI related pods
echo -e "\nPods that might be UI related (contain 'ui', 'frontend', 'web', or 'client'):"
kubectl get pods -n $NAMESPACE | grep -E 'ui|frontend|web|client'

# Get all pod labels in the namespace
echo -e "\nLabels found on pods in $NAMESPACE namespace:"
kubectl get pods -n $NAMESPACE -o json | jq -r '.items[] | .metadata.labels | to_entries[] | "\(.key)=\(.value)"' | sort | uniq

# Try to identify common app labels
echo -e "\nCommon 'app' labels:"
kubectl get pods -n $NAMESPACE -o json | jq -r '.items[] | .metadata.labels.app' | grep -v null | sort | uniq

echo -e "\nCommon 'tier' labels:"
kubectl get pods -n $NAMESPACE -o json | jq -r '.items[] | .metadata.labels.tier' | grep -v null | sort | uniq

echo -e "\nCommon 'component' labels:"
kubectl get pods -n $NAMESPACE -o json | jq -r '.items[] | .metadata.labels.component' | grep -v null | sort | uniq

# Ask user to identify UI pod
echo -e "\nPlease identify which pod is your UI pod:"
read -p "Enter the name of the UI pod: " UI_POD

if [ -z "$UI_POD" ]; then
    echo "No pod name provided. Exiting."
    exit 1
fi

# Get labels for the identified pod
echo -e "\nLabels for pod $UI_POD:"
kubectl get pod $UI_POD -n $NAMESPACE -o json | jq '.metadata.labels'

# Create helper scripts with the correct labels
APP_LABEL=$(kubectl get pod $UI_POD -n $NAMESPACE -o json | jq -r '.metadata.labels.app // "unknown"')
TIER_LABEL=$(kubectl get pod $UI_POD -n $NAMESPACE -o json | jq -r '.metadata.labels.tier // "unknown"')
COMPONENT_LABEL=$(kubectl get pod $UI_POD -n $NAMESPACE -o json | jq -r '.metadata.labels.component // "unknown"')

echo -e "\nCreating helper scripts with the correct labels..."

# Create pod_labels.sh with the correct labels
cat << EOF > pod_labels.sh
#!/bin/bash
# Pod labels for UI pods
# Generated on $(date)

# Namespace
export NAMESPACE="$NAMESPACE"

# Pod labels
export POD_APP_LABEL="$APP_LABEL"
export POD_TIER_LABEL="$TIER_LABEL"
export POD_COMPONENT_LABEL="$COMPONENT_LABEL"

# Example kubectl commands
echo "Example kubectl commands:"
echo "kubectl get pods -n \$NAMESPACE -l app=\$POD_APP_LABEL"
if [ "$TIER_LABEL" != "unknown" ]; then
    echo "kubectl get pods -n \$NAMESPACE -l tier=\$POD_TIER_LABEL"
fi
if [ "$COMPONENT_LABEL" != "unknown" ]; then
    echo "kubectl get pods -n \$NAMESPACE -l component=\$POD_COMPONENT_LABEL"
fi
EOF

chmod +x pod_labels.sh

echo -e "\nCreated pod_labels.sh with the correct labels."
echo "You can source this file to set environment variables with the correct labels:"
echo "source pod_labels.sh"

echo "=== UI pod identification complete ==="
