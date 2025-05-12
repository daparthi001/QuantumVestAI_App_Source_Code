provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.1"

  name = "eks-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

# ✅ EKS module just uses that VPC and does not create its own VPC
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

  # This enables the module to manage the aws-auth configmap
  manage_aws_auth_configmap = true

  # Option 1: Using map_additional_iam_users and map_additional_iam_roles
  # (Check module documentation for v20.8.4 if these are the exact names,
  # sometimes it's map_users / map_roles or similar)

  map_additional_iam_users = [
    {
      userarn  = "arn:aws:iam::921930869047:user/admin-user" # CORRECTED: Assuming 'admin-role' was a typo and it's a user. Or use the role mapping below.
      username = "admin"
      groups   = ["system:masters"]
    }
  ]

  map_additional_iam_roles = [
    {
      rolearn  = "arn:aws:iam::921930869047:role/your-actual-admin-role" # CRITICAL: Replace with your actual IAM role ARN
      username = "eks-admin-role"
      groups   = ["system:masters"]
    }
  ]

  # If the above map_additional_iam_users/roles are not the exact input names for v20.8.4,
  # another common pattern for this module version is:
  # aws_auth_additional_labels = {} # if you need labels
  # aws_auth_additional_annotations = {} # if you need annotations

  # And for the mappings themselves, sometimes structured like this:
  /*
  aws_auth_configmap_data = {
    mapRoles = yamlencode([
      {
        rolearn  = "arn:aws:iam::921930869047:role/your-actual-admin-role" # CRITICAL: Replace with your actual IAM role ARN
        username = "eks-admin-role"
        groups   = ["system:masters"]
      }
    ])
    mapUsers = yamlencode([
      {
        userarn  = "arn:aws:iam::921930869047:user/admin-user"
        username = "admin"
        groups   = ["system:masters"]
      }
    ])
  }
}
