# Variables for VPC configuration


variable "availability_zones" {
  description = "List of availability zones to use (defaults to the first 3 AZs in the region if empty)"
  type        = list(string)
  default     = []
}

variable "enable_vpc_flow_logs" {
  description = "Whether to enable VPC Flow Logs"
  type        = bool
  default     = true
}

variable "vpc_flow_log_retention_days" {
  description = "Number of days to retain VPC Flow Logs"
  type        = number
  default     = 30
}

variable "enable_vpc_endpoints" {
  description = "Whether to enable VPC Endpoints for AWS services"
  type        = bool
  default     = true
}

variable "vpc_endpoints_enabled" {
  description = "List of VPC endpoints to enable"
  type        = list(string)
  default     = [
    "ecr.api",
    "ecr.dkr",
    "kms",
    "logs",
    "secretsmanager",
    "sts",
    "sqs",
    "sns",
    "ssm"
  ]
}

variable "vpc_endpoint_type" {
  description = "Type of VPC endpoints to create"
  type        = string
  default     = "Interface"
}

variable "enable_public_nacl" {
  description = "Whether to create a Network ACL for public subnets"
  type        = bool
  default     = true
}

variable "enable_database_nacl" {
  description = "Whether to create a Network ACL for database subnets"
  type        = bool
  default     = true
}

variable "create_vpc" {
  description = "Whether to create a VPC"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Whether to use a single NAT Gateway for all subnets"
  type        = bool
  default     = false
}

variable "one_nat_gateway_per_az" {
  description = "Whether to use one NAT Gateway per availability zone"
  type        = bool
  default     = true
}
