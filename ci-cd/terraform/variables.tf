# AWS and Project Configuration

variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_region" {
  description = "AWS region (same as region)"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "QuantumVestAI"
}

variable "project_name" {
  description = "Project name (lowercase)"
  type        = string
  default     = "quantumvestai"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# VPC Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# EKS Cluster Configuration
variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "quantumai"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

# Node Group Configuration
variable "node_instance_type" {
  description = "Instance type for worker nodes"
  type        = string
  default     = "t3.medium"
}

variable "desired_nodes" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Maximum number of nodes in the standard node group"
  type        = number
  default     = 5
}

variable "min_nodes" {
  description = "Minimum number of nodes in the standard node group"
  type        = number
  default     = 1
}

variable "node_disk_size" {
  description = "Disk size for standard node group"
  type        = number
  default     = 50
}

# ML Node Group Variables
variable "enable_ml_nodes" {
  description = "Enable ML-specific node group"
  type        = bool
  default     = false
}

variable "ml_desired_nodes" {
  description = "Desired number of ML nodes"
  type        = number
  default     = 1
}

variable "ml_max_nodes" {
  description = "Maximum number of ML nodes"
  type        = number
  default     = 3
}

variable "ml_min_nodes" {
  description = "Minimum number of ML nodes"
  type        = number
  default     = 0
}

variable "ml_node_instance_type" {
  description = "Instance type for ML nodes"
  type        = string
  default     = "m5.xlarge"
}

variable "ml_node_disk_size" {
  description = "Disk size for ML nodes"
  type        = number
  default     = 100
}

# Domain and Certificate
variable "domain_name" {
  description = "Primary domain name for the application"
  type        = string
  default     = "quantumvestai.com"
}

# IAM and Access
variable "iam_user_arn" {
  description = "IAM user ARN for Kubernetes access"
  type        = string
  default     = "arn:aws:iam::921930869047:user/admin-user"
}

# KMS and Encryption
variable "eks_kms_cluster_name" {
  description = "Name for the EKS KMS cluster"
  type        = string
  default     = "eks-kms-cluster"
}

variable "eks_kms_role_arn" {
  description = "IAM role ARN for EKS KMS cluster"
  type        = string
  default     = null
}

# Tagging
variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}

# Data source to get current AWS account details
data "aws_caller_identity" "current" {}

# Local tags configuration
locals {
  tags = merge(
    {
      Environment = var.environment
      Project     = var.project
      ManagedBy   = "Terraform"
    },
    var.tags
  )
}

# Outputs
output "aws_account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_caller_arn" {
  description = "ARN of current AWS caller"
  value       = data.aws_caller_identity.current.arn
}