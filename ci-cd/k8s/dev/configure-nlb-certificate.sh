#!/bin/bash
# QuantumVestAI - Configure NLB Certificate
# Created: 2025-06-15 23:42:27
# Author: daparthi001

# Set variables
LB_ARN="arn:aws:elasticloadbalancing:us-east-1:921930869047:loadbalancer/net/a9b2d82d457a145599948ce733f2fd18/a0e284c610c15fa0"
CERT_ARN="arn:aws:acm:us-east-1:921930869047:certificate/94eec8e0-cf9a-4184-8e27-2c3c845c390a"
REGION="us-east-1"
APP_DOMAIN="dev.quantumvestai.com"

echo "===== Configuring ACM Certificate for NLB ====="

# Verify certificate status
echo "Verifying certificate status..."
CERT_STATUS=$(aws acm describe-certificate --certificate-arn $CERT_ARN --region $REGION --query 'Certificate.Status' --output text)
echo "Certificate status: $CERT_STATUS"

if [ "$CERT_STATUS" != "ISSUED" ]; then
  echo "ERROR: Certificate is not in ISSUED state. Cannot proceed."
  exit 1
fi

# Get the target group ARN
echo "Getting target group information..."
TARGET_GROUPS=$(aws elbv2 describe-target-groups --load-balancer-arn $LB_ARN --region $REGION --query 'TargetGroups[*].TargetGroupArn' --output text)
TARGET_GROUP_ARN=$(echo $TARGET_GROUPS | cut -d" " -f1)

if [ -z "$TARGET_GROUP_ARN" ]; then
  echo "ERROR: No target group found for the load balancer."
  exit 1
fi

echo "Target group ARN: $TARGET_GROUP_ARN"

# Check if HTTPS listener exists
echo "Checking for existing HTTPS listener..."
HTTPS_LISTENER=$(aws elbv2 describe-listeners --load-balancer-arn $LB_ARN --region $REGION --query "Listeners[?Port==\`443\`].ListenerArn" --output text)

if [ -z "$HTTPS_LISTENER" ]; then
  echo "Creating new HTTPS listener on port 443..."
  aws elbv2 create-listener \
    --load-balancer-arn $LB_ARN \
    --protocol TLS \
    --port 443 \
    --certificates CertificateArn=$CERT_ARN \
    --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
    --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN \
    --region $REGION
  
  if [ $? -eq 0 ]; then
    echo "SUCCESS: HTTPS listener created successfully."
  else
    echo "ERROR: Failed to create HTTPS listener."
    exit 1
  fi
else
  echo "Updating existing HTTPS listener..."
  aws elbv2 modify-listener \
    --listener-arn $HTTPS_LISTENER \
    --certificates CertificateArn=$CERT_ARN \
    --ssl-policy ELBSecurityPolicy-TLS13-1-2-2021-06 \
    --region $REGION
  
  if [ $? -eq 0 ]; then
    echo "SUCCESS: HTTPS listener updated successfully."
  else
    echo "ERROR: Failed to update HTTPS listener."
    exit 1
  fi
fi

# Update Ingress to use TLS
echo "Updating Ingress to use TLS..."
cat <<EOF | kubectl apply -f - --validate=false
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: quantumvestai-ingress
  namespace: dev
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /\$2
    nginx.ingress.kubernetes.io/use-regex: "true"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - $APP_DOMAIN
  rules:
  - host: $APP_DOMAIN
    http:
      paths:
      - path: /api(/|\$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: quantumvestai-dev-api
            port:
              number: 8000
      - path: /(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: ui-service
            port:
              number: 80
EOF

echo "===== NLB Certificate Configuration Complete ====="
echo ""
echo "Load Balancer DNS: a9b2d82d457a145599948ce733f2fd18-a0e284c610c15fa0.elb.us-east-1.amazonaws.com"
echo ""
echo "Next steps:"
echo "1. Update your DNS records for $APP_DOMAIN to point to the NLB hostname"
echo "2. Test HTTPS access:"
echo "   curl -k https://a9b2d82d457a145599948ce733f2fd18-a0e284c610c15fa0.elb.us-east-1.amazonaws.com --header 'Host: $APP_DOMAIN'"
echo ""
echo "For DNS setup, create a CNAME record:"
echo "$APP_DOMAIN -> a9b2d82d457a145599948ce733f2fd18-a0e284c610c15fa0.elb.us-east-1.amazonaws.com"