#!/bin/bash

# Import KMS aliases into Terraform state
echo "Importing KMS aliases into Terraform state..."

# EKS KMS alias
terraform import aws_kms_alias.eks_key_alias alias/quantumvestai-dev-eks

# CloudWatch Logs KMS alias
terraform import aws_kms_alias.cloudwatch_logs_alias alias/quantumvestai-dev-cloudwatch-logs

# S3 KMS alias
terraform import aws_kms_alias.s3_alias alias/quantumvestai-dev-s3

echo "Import complete. Now run terraform plan to verify."
