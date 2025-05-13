# Variables for ECR configuration

variable "ecr_kms_key_arn" {
  description = "ARN of KMS key for ECR encryption"
  type        = string
  default     = ""
}

variable "ecr_repository_account_ids" {
  description = "List of AWS account IDs that should have access to the ECR repository"
  type        = list(string)
  default     = []
}

variable "ecr_image_count_main" {
  description = "Number of images with 'latest' tag to keep"
  type        = number
  default     = 1
}

variable "ecr_image_count_feature" {
  description = "Number of images with feature branch tags to keep"
  type        = number
  default     = 3
}

variable "ecr_image_count_prod" {
  description = "Number of production images to keep"
  type        = number
  default     = 10
}

variable "ecr_untagged_image_days" {
  description = "Number of days to keep untagged images"
  type        = number
  default     = 7
}

variable "create_ml_model_repository" {
  description = "Whether to create a separate repository for ML model images"
  type        = bool
  default     = true
}

variable "ecr_ml_model_count" {
  description = "Number of ML model images to keep"
  type        = number
  default     = 5
}

variable "ecr_scan_notification_email" {
  description = "Email address to notify for ECR scan findings"
  type        = string
  default     = ""
}