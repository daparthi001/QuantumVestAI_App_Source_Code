# VPC Configuration for QuantumVestAI

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

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
  single_nat_gateway     = var.environment != "prod"
  one_nat_gateway_per_az = var.environment == "prod"
  
  # DNS settings
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  # VPC Flow Logs
  enable_flow_log                      = var.enable_vpc_flow_logs
  create_flow_log_cloudwatch_log_group = var.enable_vpc_flow_logs
  create_flow_log_cloudwatch_iam_role  = var.enable_vpc_flow_logs
  flow_log_max_aggregation_interval    = 60
  
  # Tags for EKS and other resources
  tags = merge(
    local.common_tags,
    {
      "kubernetes.io/cluster/${var.cluster_name}" = "shared"
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

# VPC Endpoints
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.${var.region}.s3"
  
  route_table_ids = concat(
    module.vpc.private_route_table_ids,
    module.vpc.public_route_table_ids
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-s3-vpc-endpoint-${var.environment}"
    }
  )
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = module.vpc.vpc_id
  service_name = "com.amazonaws.${var.region}.dynamodb"
  
  route_table_ids = concat(
    module.vpc.private_route_table_ids,
    module.vpc.public_route_table_ids
  )

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-dynamodb-vpc-endpoint-${var.environment}"
    }
  )
}

# VPC Endpoints for additional AWS services
resource "aws_vpc_endpoint" "services" {
  for_each = var.enable_vpc_endpoints ? toset(var.vpc_endpoints_enabled) : []

  vpc_id             = module.vpc.vpc_id
  service_name       = "com.amazonaws.${var.region}.${each.key}"
  vpc_endpoint_type  = var.vpc_endpoint_type
  private_dns_enabled = true

  security_group_ids = [aws_security_group.vpc_endpoints.id]
  subnet_ids         = module.vpc.private_subnets

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${replace(each.key, ".", "-")}-vpc-endpoint-${var.environment}"
    }
  )
}

# Security Group for VPC Endpoints
resource "aws_security_group" "vpc_endpoints" {
  name        = "${var.project_name}-vpc-endpoints-sg-${var.environment}"
  description = "Security group for VPC endpoints"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Allow HTTPS traffic from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-vpc-endpoints-sg-${var.environment}"
    }
  )
}

# Optional: Network ACLs
resource "aws_network_acl" "public" {
  count = var.enable_public_nacl ? 1 : 0

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets

  # Allow HTTP and HTTPS inbound
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 80
    to_port    = 80
  }
  
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 443
    to_port    = 443
  }
  
  # Allow ephemeral ports
  ingress {
    protocol   = "tcp"
    rule_no    = 120
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 1024
    to_port    = 65535
  }
  
  # Allow all outbound
  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-public-nacl-${var.environment}"
    }
  )
}

resource "aws_network_acl" "database" {
  count = var.enable_database_nacl ? 1 : 0

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.database_subnets

  # Allow PostgreSQL from private subnets
  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 5432
    to_port    = 5432
  }
  
  # Allow ephemeral ports
  ingress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 1024
    to_port    = 65535
  }
  
  # Allow responses back to the VPC
  egress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 1024
    to_port    = 65535
  }
  
  # Allow PostgreSQL responses
  egress {
    protocol   = "tcp"
    rule_no    = 110
    action     = "allow"
    cidr_block = var.vpc_cidr
    from_port  = 5432
    to_port    = 5432
  }
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-database-nacl-${var.environment}"
    }
  )
}

# Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_subnets" {
  description = "List of IDs of database subnets"
  value       = module.vpc.database_subnets
}

output "database_subnet_group_name" {
  description = "Name of database subnet group"
  value       = module.vpc.database_subnet_group_name
}

output "nat_public_ips" {
  description = "List of public Elastic IPs created for AWS NAT Gateway"
  value       = module.vpc.nat_public_ips
}