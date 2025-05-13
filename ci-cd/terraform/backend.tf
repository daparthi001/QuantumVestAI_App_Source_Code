# Backend configuration for Terraform state

terraform {
  backend "s3" {
    bucket         = "quantumvestai-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "quantumvestai-terraform-locks"
    encrypt        = true
  }
}