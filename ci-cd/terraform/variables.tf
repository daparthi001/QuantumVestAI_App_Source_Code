# Global Variables for QuantumVestAI Infrastructure

# Project and Environment Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "quantumvestai"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# EKS Cluster Configuration
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "quantumvestai-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.28"
}

# EKS Add-on Versions
variable "eks_addon_versions" {
  description = "Versions for EKS add-ons"
  type = object({
    vpc_cni            = string
    kube_proxy         = string
    coredns            = string
    aws_ebs_csi_driver = string
  })
  default = {
    vpc_cni            = "v1.16.0-eksbuild.1"
    kube_proxy         = "v1.28.1-eksbuild.1"
    coredns            = "v1.10.1-eksbuild.2"
    aws_ebs_csi_driver = "v1.24.0-eksbuild.1"
  }
}

# Node Group Configuration
variable "node_instance_type" {
  description = "EC2 instance type for worker nodes"
  type        = string
  default     = "t3.medium"
}

variable "desired_nodes" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 5
}

variable "min_nodes" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "node_disk_size" {
  description = "Disk size for worker nodes"
  type        = number
  default     = 50
}

# ML Node Group Configuration
variable "enable_ml_nodes" {
  description = "Enable ML-specific node group"
  type        = bool
  default     = false
}

variable "ml_node_instance_type" {
  description = "EC2 instance type for ML worker nodes"
  type        = string
  default     = "m5.xlarge"
}

variable "ml_desired_nodes" {
  description = "Desired number of ML worker nodes"
  type        = number
  default     = 1
}

variable "ml_max_nodes" {
  description = "Maximum number of ML worker nodes"
  type        = number
  default     = 3
}

variable "ml_min_nodes" {
  description = "Minimum number of ML worker nodes"
  type        = number
  default     = 0
}

variable "ml_node_disk_size" {
  description = "Disk size for ML worker nodes"
  type        = number
  default     = 100
}

# RDS Configuration
variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for RDS instance (in GB)"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance (in GB)"
  type        = number
  default     = 100
}

variable "rds_database_name" {
  description = "Name of the database to create"
  type        = string
  default     = "quantumvestai"
}

variable "rds_username" {
  description = "Username for the RDS instance"
  type        = string
  default     = "quantumvestai"
}

# Networking Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# Domain Configuration
variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = "quantumvestai.com"
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for the domain"
  type        = string
  default     = ""
}

# IAM and Authentication
variable "admin_user_arns" {
  description = "List of IAM user ARNs to grant admin access to the cluster"
  type        = list(string)
  default     = []
}

variable "developer_user_arns" {
  description = "List of IAM user ARNs to grant developer access to the cluster"
  type        = list(string)
  default     = []
}

variable "readonly_user_arns" {
  description = "List of IAM user ARNs to grant read-only access to the cluster"
  type        = list(string)
  default     = []
}

# Kubernetes Configuration
variable "environments" {
  description = "List of environments to create namespaces and RBAC for"
  type        = list(string)
  default     = ["dev", "staging", "prod"]
}

# Tagging
variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

# Locals for common tags
locals {
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags
  )
}