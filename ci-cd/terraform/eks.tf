
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "quantumvestai-cluster"
  cluster_version = "1.27"
  subnets         = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
  vpc_id          = aws_vpc.main.id

  node_groups = {
    default = {
      desired_capacity = 2
      max_capacity     = 3
      min_capacity     = 1
      instance_types   = ["t3.medium"]
    }
  }

  manage_aws_auth = true
}
