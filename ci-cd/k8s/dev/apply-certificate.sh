#!/bin/bash
# QuantumVestAI - Find and Configure NGINX Ingress Service with ACM Certificate
# Created: 2025-06-15 23:05:34
# Author: daparthi001

NAMESPACE="qvai-ingress"
CERTIFICATE_ARN="arn:aws:acm:us-east-1:921930869047:certificate/94eec8e0-cf9a-4184-8e27-2c3c845c390a"

echo "===== Finding NGINX Ingress Controller Service ====="
echo "Checking services in namespace $NAMESPACE..."
kubectl get svc -n $NAMESPACE

# Try to find the service automatically using various common labels and name patterns
SERVICE_NAME=""

# Try by label first (most reliable)
SERVICE_NAME=$(kubectl get svc -n $NAMESPACE -l app.kubernetes.io/name=ingress-nginx -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

# If not found, try common naming patterns
if [ -z "$SERVICE_NAME" ]; then
  for pattern in "nginx-controller" "ingress-controller" "ingress-nginx-controller" "nginx-ingress-controller"; do
    FOUND=$(kubectl get svc -n $NAMESPACE | grep $pattern | awk '{print $1}' | head -1)
    if [ -n "$FOUND" ]; then
      SERVICE_NAME=$FOUND
      break
    fi
  done
fi

# If still not found, try any LoadBalancer service
if [ -z "$SERVICE_NAME" ]; then
  SERVICE_NAME=$(kubectl get svc -n $NAMESPACE --field-selector type=LoadBalancer -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
fi

if [ -z "$SERVICE_NAME" ]; then
  echo "===== ERROR: No suitable NGINX Ingress Controller service found ====="
  echo "It seems the NGINX Ingress Controller is not properly installed."
  echo "You might need to reinstall it."
  exit 1
fi

echo "===== Found service: $SERVICE_NAME ====="
echo "Applying ACM certificate to service..."

kubectl patch svc $SERVICE_NAME -n $NAMESPACE -p '{
  "metadata": {
    "annotations": {
      "service.beta.kubernetes.io/aws-load-balancer-ssl-cert": "'$CERTIFICATE_ARN'",
      "service.beta.kubernetes.io/aws-load-balancer-backend-protocol": "http",
      "service.beta.kubernetes.io/aws-load-balancer-ssl-ports": "443"
    }
  }
}'

if [ $? -eq 0 ]; then
  echo "===== SUCCESS: Certificate applied to service $SERVICE_NAME ====="
  echo "Certificate ARN: $CERTIFICATE_ARN"
  echo "It may take a few minutes for the changes to propagate to the load balancer."
else
  echo "===== ERROR: Failed to apply certificate to service ====="
fi

# Get the load balancer URL for reference
EXTERNAL_IP=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
if [ -n "$EXTERNAL_IP" ]; then
  echo "Load Balancer Address: $EXTERNAL_IP"
  echo "You can test your SSL setup with:"
  echo "curl -k https://$EXTERNAL_IP"
fi

echo "===== Complete ====="