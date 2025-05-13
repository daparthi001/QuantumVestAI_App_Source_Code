# Project Configuration
project_name = "quantumvestai"
environment  = "dev"
region       = "us-east-1"

# EKS Cluster Configuration
cluster_name         = "quantumvestai-dev-cluster"
kubernetes_version   = "1.28"

# Node Group Configuration
node_instance_type = "t3.medium"
desired_nodes      = 2
max_nodes          = 5
min_nodes          = 1

# ML Node Group Configuration
enable_ml_nodes        = true
ml_node_instance_type  = "m5.xlarge"
ml_desired_nodes       = 1
ml_max_nodes           = 3

# RDS Configuration
rds_instance_class         = "db.t3.medium"
rds_allocated_storage      = 20
rds_max_allocated_storage  = 100
rds_database_name          = "quantumvestai_dev"
rds_username               = "quantumvestai_dev_user"

# Networking
vpc_cidr = "10.0.0.0/16"

# Domain Configuration
domain_name      = "quantumvestai.com"
route53_zone_id  = "" # Optional: Provide existing zone ID if available

# IAM and Authentication
admin_user_arns = [
  "arn:aws:iam::123456789012:user/admin-user"
]

developer_user_arns = [
  "arn:aws:iam::123456789012:user/dev-user1",
  "arn:aws:iam::123456789012:user/dev-user2"
]

readonly_user_arns = [
  "arn:aws:iam::123456789012:user/readonly-user"
]

# Additional Tags
tags = {
  Project     = "QuantumVestAI"
  Environment = "Development"
  Managed     = "Terraform"
  CostCenter  = "ML-Infrastructure"
}