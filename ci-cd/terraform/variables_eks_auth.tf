# Variables for EKS authentication

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

variable "additional_iam_roles_for_auth" {
  description = "Additional IAM roles to add to the aws-auth ConfigMap"
  type = list(object({
    rolearn  = string
    username = string
    groups   = list(string)
  }))
  default = []
}


