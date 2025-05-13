variable "region" {
  default     = "us-east-1"
  description = "AWS region"
}

variable "cluster_name" {
  default     = "quantumai"
  description = "EKS cluster name"
}

variable "node_instance_type" {
  default     = "t3.medium"
  description = "Instance type for worker nodes"
}

variable "desired_nodes" {
  default     = 1
  description = "Desired number of worker nodes"
}

variable "iam_user_arn" {
  default     = "arn:aws:iam::921930869047:user/admin-user" # Replace with actual IAM user ARN
  description = "IAM user ARN for Kubernetes access"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "QuantumVestAI"
}

# Common tags to be applied to all resources
locals {
  tags = {
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "Terraform"
  }
}