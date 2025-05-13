# VPC Configuration for QuantumVestAI

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  # Basic VPC configuration
  name = "${var.project_name}-vpc-${var.environment}"
  cidr = var.vpc_cidr

  # Use all available AZs in the region if not specified
  azs = length(var.availability_zones) > 0 ? var.availability_zones : [
    "${var.region}a", 
    "${var.region}b", 
    "${var.region}c"
  ]

  # Subnets configuration
  private_subnets = [
    cidrsubnet(var.vpc_cidr, 4, 0),
    cidrsubnet(var.vpc_cidr, 4, 1),
    cidrsubnet(var.vpc_cidr, 4, 2)
  ]
  
  public_subnets = [
    cidrsubnet(var.vpc_cidr, 4, 4),
    cidrsubnet(var.vpc_cidr, 4, 5), 
    cidrsubnet(var.vpc_cidr, 4, 6)
  ]
  
  # Database subnets for RDS
  database_subnets = [
    cidrsubnet(var.vpc_cidr, 4, 8),
    cidrsubnet(var.vpc_cidr, 4, 9),
    cidrsubnet(var.vpc_cidr, 4, 10)
  ]
  
  # Create separate route tables for each subnet
  create_database_subnet_group       = true
  create_database_subnet_route_table = true
  
  # NAT Gateway configuration
  enable_nat_gateway     = true
  single_nat_gateway     = var.environment != "prod" # Use single NAT for non-prod environments
  one_nat_gateway_per_az = var.environment == "prod" # Use multiple NATs for production
  
  # DNS settings
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # VPC Flow Logs for network monitoring
  enable_flow_log                      = var.enable_vpc_flow_logs
  create_flow_log_cloudwatch_log_group = var.enable_vpc_flow_logs
  create_flow_log_cloudwatch_iam_role  = var.enable_vpc_flow_logs
  flow_log_max_aggregation_interval    = 60

  # Tags for EKS and other resources
  tags = merge(
    local.tags,
    {
      Name                                         = "${var.project_name}-vpc-${var.environment}"
      "kubernetes.io/cluster/${var.cluster_name}"  = "shared"
    }
  )

  # Tags for public subnets (required for ALB integration)
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  # Tags for private subnets (required for internal ALB)
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
  
  # Tags for database subnets
  database_subnet_tags = {
    "purpose" = "database"
  }
}

# Rest of the file remains the same as in the previous artifact