# Variables for KMS encryption

variable "kms_deletion_window_in_days" {
  description = "The waiting period before a KMS key is deleted"
  type        = number
  default     = 7
}

variable "enable_kms_key_rotation" {
  description = "Whether to enable automatic rotation of KMS keys"
  type        = bool
  default     = true
}

variable "encrypt_eks_secrets" {
  description = "Whether to encrypt EKS secrets using KMS"
  type        = bool
  default     = true
}

variable "encrypt_rds_storage" {
  description = "Whether to encrypt RDS storage using KMS"
  type        = bool
  default     = true
}

variable "encrypt_secrets_manager" {
  description = "Whether to encrypt Secrets Manager secrets using KMS"
  type        = bool
  default     = true
}

# Note: These variables can be used to conditionally enable/disable encryption
# for different environments (e.g., you might want to skip KMS encryption 
# in development environments to reduce costs)