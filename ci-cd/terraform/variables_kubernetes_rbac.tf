# Variables for Kubernetes RBAC configuration

variable "environments" {
  description = "List of environments to create namespaces and RBAC for"
  type        = list(string)
  default     = ["dev", "staging", "prod"]
}

variable "user_role_bindings" {
  description = "List of user role bindings"
  type = list(object({
    username = string
    role     = string  # Can be "readonly", "developer", "ml-engineer", or "admin"
  }))
  default = [
    {
      username = "readonly-user"
      role     = "readonly"
    },
    {
      username = "developer-user"
      role     = "developer"
    },
    {
      username = "ml-user"
      role     = "ml-engineer"
    },
    {
      username = "admin-user"
      role     = "admin"
    }
  ]
}

variable "component_iam_roles" {
  description = "IAM roles for application components for IRSA"
  type        = map(string)
  default     = {
    "api"            = ""  # Will be populated with the actual role ARN
    "model-training" = ""  # Will be populated with the actual role ARN
    "scheduler"      = ""  # Will be populated with the actual role ARN
  }
}

variable "create_namespaces" {
  description = "Whether to create the namespaces or use existing ones"
  type        = bool
  default     = true
}
