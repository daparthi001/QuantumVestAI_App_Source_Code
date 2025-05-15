#!/bin/bash

# This script creates Kubernetes secrets from environment files
# It should be run on your local machine, not in the container

# Check if .env.secrets file exists
if [ ! -f ".env.secrets" ]; then
    echo "Error: .env.secrets file not found"
    exit 1
fi

# Read secrets from file and create base64 encoded values
echo "Creating Kubernetes secrets..."

# Create a temporary file for the secrets YAML
cat > temp-secrets.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: ui-secrets
type: Opaque
data:
EOF

# Add each secret as a base64 encoded value
while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    [[ $key =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    
    # Encode the value in base64
    encoded_value=$(echo -n "$value" | base64)
    
    # Add to YAML file
    echo "  $key: $encoded_value" >> temp-secrets.yaml
done < .env.secrets

# Apply the secrets to Kubernetes
kubectl apply -f temp-secrets.yaml
rm temp-secrets.yaml

echo "Secrets created successfully"