# Backend configuration for Terraform state
# Initially using local state until S3 bucket is created

# Uncomment this block after creating the S3 bucket and DynamoDB table
# terraform {
#   backend "s3" {
#     bucket         = "quantumvestai-terraform-state"
#     key            = "infrastructure/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "quantumvestai-terraform-locks"
#     encrypt        = true
#   }
# }