module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.4"

  cluster_name    = var.cluster_name
  cluster_version = "1.29"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      desired_size = 2
      max_size     = 3
      min_size     = 1

      instance_types = ["t3.medium"]
    }
  }

  cluster_encryption_config = {
    resources        = ["secrets"]
    provider_key_arn = aws_kms_key.eks_key.arn
  }
}

# #✅ aws_auth is now its own module block
module "aws_auth" {
  source  = "terraform-aws-modules/eks/aws//modules/aws-auth"
  version = "20.8.4"

  cluster_name = module.eks.cluster_name

  map_users = [
    {
      userarn  = "arn:aws:iam::921930869047:user/admin-role"
      username = "admin"
      groups   = ["system:masters"]
    }
  ]

  map_roles = [
    {
      rolearn  = "arn:aws:iam::921930869047:role/quantumai"
      username = "eks-admin-role"
      groups   = ["system:masters"]
    }
  ]
}
