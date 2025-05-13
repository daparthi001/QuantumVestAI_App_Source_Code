# Local variables used throughout the configuration

locals {
  # Remove common_tags as they're now in the provider's default_tags
  
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