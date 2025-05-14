# Terraform Backend Configuration
# Created: 2025-05-14 01:03:28
# Author: daparthi001

terraform {
  backend "s3" {
    bucket         = "quantumvestai-terraform-state"
    key            = "resources/terraform.tfstate"
    region         = "us-east-1"  # Update this if using a different region
    encrypt        = true
    dynamodb_table = "quantumvestai-terraform-locks"
  }
}