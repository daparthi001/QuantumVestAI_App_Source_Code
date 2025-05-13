# Local variables used throughout the configuration

locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "QuantumVestAI"
    CreatedBy   = "daparthi001"
    CreatedAt   = "2025-05-13"
  }

  # EKS Authentication - used in eks-auth.tf
  map_roles = [
    # Add any predefined role mappings here
  ]

  map_users = concat(
    [
      for arn in var.admin_user_arns : {
        userarn  = arn
        username = split("/", arn)[1]
        groups   = ["system:masters"]
      }
    ],
    [
      for arn in var.developer_user_arns : {
        userarn  = arn
        username = split("/", arn)[1]
        groups   = ["${var.cluster_name}-developers"]
      }
    ],
    [
      for arn in var.readonly_user_arns : {
        userarn  = arn
        username = split("/", arn)[1]
        groups   = ["${var.cluster_name}-readonly"]
      }
    ]
  )

  # Security groups and other shared resources
  eks_pod_subnets = module.vpc.private_subnets
  
  # Additional local variables as needed
}