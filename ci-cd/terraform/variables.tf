# Main Variables File

# General variables
variable "region" {
  description = "AWS Region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "quantumvestai"
}

# Keep other variables that don't duplicate with specialized variable files

# Remove these duplicates:
# variable "eks_addon_versions" { ... } # - In variables-eks-addons.tf
# variable "rds_instance_class" { ... } # - In variables-rds.tf
# variable "rds_allocated_storage" { ... } # - In variables-rds.tf
# variable "rds_max_allocated_storage" { ... } # - In variables-rds.tf
# variable "rds_database_name" { ... } # - In variables-rds.tf
# variable "rds_username" { ... } # - In variables-rds.tf
# variable "route53_zone_id" { ... } # - In variables-cloudfront.tf
# variable "admin_user_arns" { ... } # - Keep here, remove from variables_eks_auth.tf
# variable "developer_user_arns" { ... } # - Keep here, remove from variables_eks_auth.tf
# variable "readonly_user_arns" { ... } # - Keep here, remove from variables_eks_auth.tf
# variable "environments" { ... } # - Keep here, remove from variables_kubernetes_rbac.tf

# Retain the variable blocks for:
variable "admin_user_arns" {
  description = "ARNs of IAM users/roles for EKS admin access"
  type        = list(string)
  default     = []
}

variable "developer_user_arns" {
  description = "ARNs of IAM users/roles for EKS developer access"
  type        = list(string)
  default     = []
}

variable "readonly_user_arns" {
  description = "ARNs of IAM users/roles for EKS read-only access"
  type        = list(string)
  default     = []
}

variable "environments" {
  description = "List of environments for RBAC"
  type        = list(string)
  default     = ["dev", "staging", "prod"]
}

# Keep the rest of non-duplicated variables