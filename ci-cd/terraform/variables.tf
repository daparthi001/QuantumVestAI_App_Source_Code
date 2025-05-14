# Main variables file - consolidated across the project

# General
variable "region" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "quantumvestai"
}

# Networking variables
variable "vpc_cidr" {
  description = "CIDR for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# EKS variables
variable "cluster_name" {
  description = "Name of EKS cluster"
  type        = string
  default     = "quantumvestai-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.31"
}

variable "node_instance_type" {
  description = "EC2 instance type for EKS nodes"
  type        = string
  default     = "t3.medium"
}

variable "node_disk_size" {
  description = "Disk size for EKS nodes in GB"
  type        = number
  default     = 100
}

variable "min_nodes" {
  description = "Minimum number of nodes"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of nodes"
  type        = number
  default     = 5
}

variable "desired_nodes" {
  description = "Desired number of nodes"
  type        = number
  default     = 2
}

# EKS ML nodes
variable "enable_ml_nodes" {
  description = "Whether to create ML-specific node group"
  type        = bool
  default     = false
}

variable "ml_node_instance_type" {
  description = "EC2 instance type for ML nodes"
  type        = string
  default     = "g4dn.xlarge"
}

variable "ml_node_disk_size" {
  description = "Disk size for ML nodes in GB"
  type        = number
  default     = 200
}

variable "ml_min_nodes" {
  description = "Minimum number of ML nodes"
  type        = number
  default     = 0
}

variable "ml_max_nodes" {
  description = "Maximum number of ML nodes"
  type        = number
  default     = 3
}

variable "ml_desired_nodes" {
  description = "Desired number of ML nodes"
  type        = number
  default     = 0
}

# EKS add-ons configuration
variable "eks_addon_versions" {
  description = "Map of EKS addon names to versions"
  type        = map(string)
  default     = {
    "coredns"            = "v1.9.3-eksbuild.2"
    "kube-proxy"         = "v1.26.2-eksbuild.1"
    "vpc-cni"            = "v1.12.2-eksbuild.1"
    "aws-ebs-csi-driver" = "v1.16.0-eksbuild.1"
  }
}

# RDS variables
variable "rds_instance_class" {
  description = "Instance class for RDS"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "Max allocated storage for RDS in GB"
  type        = number
  default     = 100
}

variable "rds_database_name" {
  description = "Name of the database"
  type        = string
  default     = "quantumvestaidb"
}

variable "rds_username" {
  description = "Master username for RDS"
  type        = string
  default     = "dbadmin"
}

# Storage variables
variable "model_storage_bucket" {
  description = "S3 bucket name for storing ML models"
  type        = string
  default     = "quantumvestai-ml-models"
}

# Domain and DNS
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "quantumvestai.com"
}

variable "route53_zone_id" {
  description = "Route53 zone ID for the domain"
  type        = string
  default     = "Z00140672OE92YR0CD3MZ"
}

# CloudFront
variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}

# Load balancer
variable "alb_internal" {
  description = "Whether ALB is internal or internet-facing"
  type        = bool
  default     = false
}

# Authentication variables
variable "admin_user_arns" {
  description = "ARNs of IAM users/roles for EKS admin access"
  type        = list(string)
  default     = ["arn:aws:iam::921930869047:user/admin-role"]
}

variable "developer_user_arns" {
  description = "ARNs of IAM users/roles for EKS developer access"
  type        = list(string)
  default     = []
}

variable "readonly_user_arns" {
  description = "ARNs of IAM users/roles for EKS read-only access"
  type        = list(string)
  default     = ["arn:aws:iam::921930869047:user/admin-role",]
}

variable "environments" {
  description = "List of environments for RBAC"
  type        = list(string)
  default     = ["dev", "staging", "prod"]
}

# Optional features
variable "output_kubeconfig_update_script" {
  description = "Whether to output kubeconfig update script"
  type        = bool
  default     = true
}

variable "elb_account_ids" {
  description = "Map of AWS regions to ELB account IDs for ALB access logs"
  type        = map(string)
  default     = {
    "us-east-1"      = "127311923021"
    "us-east-2"      = "033677994240"
    "us-west-1"      = "027434742980"
    "us-east-1"      = "797873946194"
    "af-south-1"     = "098369216593"
    "ap-east-1"      = "754344448648"
    "ap-northeast-1" = "582318560864"
    "ap-northeast-2" = "600734575887"
    "ap-northeast-3" = "383597477331"
    "ap-south-1"     = "718504428378"
    "ap-southeast-1" = "114774131450"
    "ap-southeast-2" = "783225319266"
    "ap-southeast-3" = "589379963580"
    "ca-central-1"   = "985666609251"
    "eu-central-1"   = "054676820928"
    "eu-north-1"     = "897822967062"
    "eu-south-1"     = "635631232127"
    "eu-west-1"      = "156460612806"
    "eu-west-2"      = "652711504416"
    "eu-west-3"      = "009996457667"
    "me-south-1"     = "076674570225"
    "sa-east-1"      = "507241528517"
  }
}