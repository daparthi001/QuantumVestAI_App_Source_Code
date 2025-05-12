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

  # This enables the module to manage the aws-auth configmap. This IS a valid argument.
  manage_aws_auth_configmap = true

  # THESE ARE THE CORRECTED ARGUMENT NAMES FOR v20.8.4
  aws_auth_additional_user_mapping = [
    {
      userarn  = "arn:aws:iam::921930869047:user/admin-user" # ### REPLACE with your actual IAM USER ARN ###
      username = "admin" # Kubernetes username
      groups   = ["system:masters"]
    }
  ]

  aws_auth_additional_role_mapping = [
    {
      rolearn  = "arn:aws:iam::921930869047:role/your-actual-admin-role" # ### CRITICAL: REPLACE with your actual IAM ROLE ARN ###
      username = "eks-admin-role" # Kubernetes username
      groups   = ["system:masters"]
    }
  ]

  # Remove or comment out any lines that look like:
  # map_additional_iam_users = [ ... ]
  # map_additional_iam_roles = [ ... ]
  # And remove the commented-out sections like /* aws_auth_configmap_data = { ... } */
  # unless you intend to use them specifically (which we are not doing right now).
}
