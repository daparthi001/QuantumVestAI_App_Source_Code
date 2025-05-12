terraform {
  backend "s3" {
    bucket         = "quantumvestai-state-bucket"
    key            = "quantumvestai/eks/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "quantumvestai-lock-table"
    encrypt        = true
  }
}