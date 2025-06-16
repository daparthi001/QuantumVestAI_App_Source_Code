#!/bin/bash
# QuantumVestAI - Migrate from NGINX Ingress to AWS ALB
# Created: 2025-06-16 00:19:09
# Author: daparthi001

echo "===== Migrating from NGINX Ingress to AWS ALB ====="

# Step 1: Get EKS cluster info
echo "Getting EKS cluster info..."
EKS_CLUSTER_NAME=$(aws eks list-clusters --query 'clusters[0]' --output text)
if [ -z "$EKS_CLUSTER_NAME" ]; then
  echo "ERROR: No EKS clusters found. Please enter your cluster name:"
  read -r EKS_CLUSTER_NAME
fi
echo "Using EKS cluster: $EKS_CLUSTER_NAME"

# Get VPC ID
echo "Getting VPC ID..."
VPC_ID=$(aws eks describe-cluster --name $EKS_CLUSTER_NAME --query 'cluster.resourcesVpcConfig.vpcId' --output text)
if [ -z "$VPC_ID" ]; then
  echo "ERROR: Could not determine VPC ID. Please enter your VPC ID:"
  read -r VPC_ID
fi
echo "Using VPC ID: $VPC_ID"

# Step 2: Install the AWS Load Balancer Controller
echo "Adding EKS Helm repo..."
helm repo add eks https://aws.github.io/eks-charts
helm repo update

echo "Checking if AWS Load Balancer Controller is already installed..."
if helm list -n kube-system | grep -q aws-load-balancer-controller; then
  echo "AWS Load Balancer Controller is already installed."
else
  echo "Creating IAM OIDC provider for EKS..."
  eksctl utils associate-iam-oidc-provider \
    --region us-east-1 \
    --cluster $EKS_CLUSTER_NAME \
    --approve

  echo "Creating IAM policy for AWS Load Balancer Controller..."
  POLICY_ARN=$(aws iam list-policies --query 'Policies[?PolicyName==`AWSLoadBalancerControllerIAMPolicy`].Arn' --output text)
  
  if [ -z "$POLICY_ARN" ]; then
    echo "Downloading IAM policy document..."
    curl -o iam-policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
    
    echo "Creating IAM policy..."
    POLICY_ARN=$(aws iam create-policy \
      --policy-name AWSLoadBalancerControllerIAMPolicy \
      --policy-document file://iam-policy.json \
      --query 'Policy.Arn' --output text)
    
    rm iam-policy.json
  fi
  
  echo "Policy ARN: $POLICY_ARN"
  
  echo "Creating IAM service account for AWS Load Balancer Controller..."
  eksctl create iamserviceaccount \
    --cluster=$EKS_CLUSTER_NAME \
    --namespace=kube-system \
    --name=aws-load-balancer-controller \
    --attach-policy-arn=$POLICY_ARN \
    --override-existing-serviceaccounts \
    --approve
  
  echo "Installing AWS Load Balancer Controller..."
  helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=$EKS_CLUSTER_NAME \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller \
    --set region=us-east-1 \
    --set vpcId=$VPC_ID
fi

# Step 3: Wait for controller to be ready
echo "Waiting for AWS Load Balancer Controller to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/aws-load-balancer-controller -n kube-system

# Step 4: Create ALB Ingress
echo "Creating ALB Ingress for QuantumVestAI application..."
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: quantumvestai-alb
  namespace: dev
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:921930869047:certificate/94eec8e0-cf9a-4184-8e27-2c3c845c390a
    alb.ingress.kubernetes.io/ssl-redirect: '443'
    alb.ingress.kubernetes.io/group.name: "quantumvestai"
    alb.ingress.kubernetes.io/healthcheck-path: "/"
    alb.ingress.kubernetes.io/success-codes: "200,404"
spec:
  rules:
  - host: dev.quantumvestai.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: quantumvestai-dev-api
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ui-service
            port:
              number: 80
EOF

# Step 5: Verify services
echo "Verifying services..."
kubectl get svc -n dev

# Step 6: Wait for ALB to be provisioned
echo "Waiting for ALB to be provisioned (this may take several minutes)..."
sleep 30

# Check every 30 seconds for up to 10 minutes
for i in {1..20}; do
  echo "Checking ALB status (attempt $i/20)..."
  ALB_HOSTNAME=$(kubectl get ingress quantumvestai-alb -n dev -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
  
  if [ -n "$ALB_HOSTNAME" ]; then
    echo "ALB has been provisioned!"
    echo "ALB Hostname: $ALB_HOSTNAME"
    break
  fi
  
  if [ $i -eq 20 ]; then
    echo "Timed out waiting for ALB to be provisioned. Check status manually with:"
    echo "kubectl get ingress quantumvestai-alb -n dev"
  else
    echo "ALB is still being provisioned. Waiting 30 seconds..."
    sleep 30
  fi
done

# Step 7: Clean up NGINX Ingress (optional)
echo "Would you like to remove the NGINX Ingress resources? (yes/no)"
read -r REMOVE_NGINX

if [ "$REMOVE_NGINX" = "yes" ]; then
  echo "Removing NGINX Ingress resources..."
  kubectl delete ingress quantumvestai-ingress -n dev || echo "Ingress quantumvestai-ingress not found"
  kubectl delete ingress quantumvestai-ingress-simple -n dev || echo "Ingress quantumvestai-ingress-simple not found"
  kubectl delete ingress minimal-ingress -n dev || echo "Ingress minimal-ingress not found"
  
  echo "Would you like to remove the NGINX Ingress Controller as well? (yes/no)"
  read -r REMOVE_CONTROLLER
  
  if [ "$REMOVE_CONTROLLER" = "yes" ]; then
    echo "Removing NGINX Ingress Controller..."
    kubectl delete namespace ingress-nginx
  fi
fi

echo "===== Migration Complete ====="
echo ""
if [ -n "$ALB_HOSTNAME" ]; then
  echo "Your application is now accessible via the ALB:"
  echo "ALB Hostname: $ALB_HOSTNAME"
  echo ""
  echo "Next steps:"
  echo "1. Update your DNS to point dev.quantumvestai.com to $ALB_HOSTNAME"
  echo "2. Test HTTPS access: https://dev.quantumvestai.com/"
else
  echo "ALB is still being provisioned. Check status with:"
  echo "kubectl get ingress quantumvestai-alb -n dev"
  echo ""
  echo "Once the ALB is ready, update your DNS to point dev.quantumvestai.com to the ALB hostname"
fi