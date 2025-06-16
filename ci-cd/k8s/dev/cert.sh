#!/bin/bash
# QuantumVestAI AWS ACM Certificate Creation Script
# Created: 2025-06-15 16:07:46
# Author: daparthi001

# Configuration - MODIFY THESE VALUES
DOMAIN_NAME="dev.quantumvestai.com"
REGION="us-east-1"
PROJECT="quantumvestai"
ENVIRONMENT="development"
AWS_PROFILE="default"  # Change this if you're using a specific AWS profile

# Script requires AWS CLI v2
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check AWS CLI version
AWS_VERSION=$(aws --version | cut -d ' ' -f1 | cut -d '/' -f2 | cut -d '.' -f1)
if [ "$AWS_VERSION" -lt 2 ]; then
    echo "AWS CLI version 2 or higher is required. Please upgrade."
    exit 1
fi

# Set AWS profile if specified
if [ "$AWS_PROFILE" != "default" ]; then
    export AWS_PROFILE="$AWS_PROFILE"
    echo "Using AWS Profile: $AWS_PROFILE"
fi

echo "===== Creating ACM Certificate for $DOMAIN_NAME ====="

# Request the certificate
echo "Requesting certificate..."
CERTIFICATE_ARN=$(aws acm request-certificate \
    --domain-name "$DOMAIN_NAME" \
    --validation-method DNS \
    --tags Key=Project,Value="$PROJECT" Key=Environment,Value="$ENVIRONMENT" Key=CreatedBy,Value="daparthi001" Key=CreatedDate,Value="2025-06-15" \
    --region "$REGION" \
    --output text)

if [ -z "$CERTIFICATE_ARN" ]; then
    echo "Failed to request certificate."
    exit 1
fi

echo "Certificate requested successfully: $CERTIFICATE_ARN"

# Wait for a moment for the certificate to be created
echo "Waiting for certificate to be processed..."
sleep 5

# Get the validation details
echo "Getting validation details..."
VALIDATION_DATA=$(aws acm describe-certificate \
    --certificate-arn "$CERTIFICATE_ARN" \
    --region "$REGION" \
    --query "Certificate.DomainValidationOptions[0]")

# Extract validation information
VALIDATION_DOMAIN=$(echo "$VALIDATION_DATA" | jq -r '.ValidationDomain // .ResourceRecord.Name')
VALIDATION_NAME=$(echo "$VALIDATION_DATA" | jq -r '.ResourceRecord.Name')
VALIDATION_VALUE=$(echo "$VALIDATION_DATA" | jq -r '.ResourceRecord.Value')
VALIDATION_TYPE=$(echo "$VALIDATION_DATA" | jq -r '.ResourceRecord.Type')

if [ -z "$VALIDATION_NAME" ] || [ -z "$VALIDATION_VALUE" ] || [ "$VALIDATION_NAME" == "null" ]; then
    echo "Failed to get validation details. Please try again in a moment."
    echo "Certificate ARN: $CERTIFICATE_ARN"
    exit 1
fi

echo "===== DNS Validation Information ====="
echo "Domain: $DOMAIN_NAME"
echo "Certificate ARN: $CERTIFICATE_ARN"
echo "You need to create the following DNS record to validate your certificate:"
echo "Record Name: $VALIDATION_NAME"
echo "Record Type: $VALIDATION_TYPE"
echo "Record Value: $VALIDATION_VALUE"
echo ""

# Check if the domain is managed by Route 53
HOSTED_ZONES=$(aws route53 list-hosted-zones --output json)
DOMAIN_PARTS=$(echo "$DOMAIN_NAME" | tr '.' ' ' | tac)
HOSTED_ZONE_ID=""

# Try to find a matching hosted zone
for part in $DOMAIN_PARTS; do
    for zone in $(echo "$HOSTED_ZONES" | jq -r '.HostedZones[] | .Name + ":" + .Id'); do
        ZONE_NAME=$(echo "$zone" | cut -d':' -f1 | sed 's/.$//')
        ZONE_ID=$(echo "$zone" | cut -d':' -f2 | sed 's/\/hostedzone\///')
        
        if [[ "$DOMAIN_NAME" == *"$ZONE_NAME"* ]]; then
            HOSTED_ZONE_ID="$ZONE_ID"
            HOSTED_ZONE_NAME="$ZONE_NAME"
            break 2
        fi
    done
done

# If domain is managed by Route 53, offer to create the validation record
if [ -n "$HOSTED_ZONE_ID" ]; then
    echo "Found matching Route 53 Hosted Zone: $HOSTED_ZONE_NAME (ID: $HOSTED_ZONE_ID)"
    echo "Would you like to automatically create the validation record in Route 53? (y/n)"
    read -r CREATE_RECORD

    if [[ "$CREATE_RECORD" =~ ^[Yy]$ ]]; then
        echo "Creating DNS validation record..."
        
        # Create change batch JSON file
        CHANGE_BATCH=$(cat <<EOF
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "$VALIDATION_NAME",
        "Type": "$VALIDATION_TYPE",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "$VALIDATION_VALUE"
          }
        ]
      }
    }
  ]
}
EOF
)
        
        # Apply the change
        aws route53 change-resource-record-sets \
            --hosted-zone-id "$HOSTED_ZONE_ID" \
            --change-batch "$CHANGE_BATCH"
        
        echo "DNS validation record created successfully!"
        echo "Certificate validation will begin automatically."
        echo "It may take up to 30 minutes for validation to complete."
    else
        echo "Please create the DNS validation record manually."
    fi
else
    echo "No matching Route 53 Hosted Zone found."
    echo "Please create the DNS validation record manually in your DNS provider."
fi

echo ""
echo "===== Next Steps ====="
echo "1. Ensure the DNS validation record is created."
echo "2. Check certificate status using:"
echo "   aws acm describe-certificate --certificate-arn $CERTIFICATE_ARN --region $REGION"
echo "3. Once issued, update your NGINX Ingress configuration with the certificate ARN."
echo ""
echo "Example Helm upgrade command (adjust as needed):"
echo "helm upgrade qvai-nginx ingress-nginx/ingress-nginx \\"
echo "  --namespace qvai-ingress \\"
echo "  --set controller.service.annotations.\"service\\.beta\\.kubernetes\\.io/aws-load-balancer-ssl-cert\"=\"$CERTIFICATE_ARN\" \\"
echo "  --set controller.service.annotations.\"service\\.beta\\.kubernetes\\.io/aws-load-balancer-backend-protocol\"=http \\"
echo "  --set controller.service.annotations.\"service\\.beta\\.kubernetes\\.io/aws-load-balancer-ssl-ports\"=https \\"
echo "  --reuse-values"
echo ""
echo "Example kubectl patch command:"
echo "kubectl patch svc qvai-nginx-controller -n qvai-ingress -p '{\"metadata\":{\"annotations\":{\"service.beta.kubernetes.io/aws-load-balancer-ssl-cert\":\"$CERTIFICATE_ARN\"}}}'"

# Save the certificate info to a file
{
    echo "# QuantumVestAI ACM Certificate Info"
    echo "# Created: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo "DOMAIN_NAME=$DOMAIN_NAME"
    echo "CERTIFICATE_ARN=$CERTIFICATE_ARN"
    echo "REGION=$REGION"
} > quantumvestai-cert-info.txt

echo "Certificate information saved to quantumvestai-cert-info.txt"