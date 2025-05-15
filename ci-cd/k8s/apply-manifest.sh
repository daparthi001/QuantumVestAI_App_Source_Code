#!/bin/bash
# Script to deploy database configuration to a specific environment

# Set environment
ENV="dev"  # Change to "staging" or "prod" as needed

# Create environment namespace if it doesn't exist
#kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -

# Copy RDS credentials secret from default namespace to environment namespace
kubectl get secret quantumvestai-cluster-rds-credentials -n default -o yaml | \
  sed "s/namespace: default/namespace: dev/" | \
  sed '/resourceVersion:/d' | \
  sed '/uid:/d' | \
  sed '/creationTimestamp:/d' | \
  sed '/selfLink:/d' | \
  sed '/"kubernetes.io"/d' | \
  kubectl apply -f -

# Create temporary directory
TEMP_DIR=$(mktemp -d)

# For each YAML file, replace dev and apply
for file in db-backup-pvc.yaml db-backup-cronjob.yaml db-init-job.yaml db-init-configmap.yaml; do
  echo "Processing $file..."
  sed "s/dev/$ENV/g" $file > $TEMP_DIR/$file
  kubectl apply -f $TEMP_DIR/$file
done

# Clean up
rm -rf $TEMP_DIR

echo "Database configuration deployed to the dev namespace."
echo "You can check the status with: kubectl get all -n dev"