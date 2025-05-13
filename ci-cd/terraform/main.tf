# QuantumVestAI Infrastructure

# Local variables
locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Module imports and other configurations that aren't duplicated
# Keep any unique resources that don't conflict with other files

# Remove the duplicate:
# - terraform block with required_providers
# - backend "s3" block
# - provider "aws" block
# - provider "kubernetes" block 
# - provider "helm" block
# - data "aws_caller_identity" "current" block

# Keep only unique outputs if any
output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "region" {
  description = "AWS Region"
  value       = var.region
}