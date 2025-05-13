# Consolidated Output Definitions

# General outputs
# Remove duplicate outputs that are already in main.tf

# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

# EKS Outputs
# Keep outputs from eks_cluster.tf that aren't duplicated elsewhere

# Load Balancer Outputs
# Remove duplicates with loadbalancer.tf
# output "alb_dns_name" { ... } - Already in loadbalancer.tf
# output "alb_zone_id" { ... } - Already in loadbalancer.tf
# output "target_group_arn" { ... } - Already in loadbalancer.tf

# RDS Outputs
output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.main.endpoint
}

output "rds_port" {
  description = "Port of the RDS instance"
  value       = aws_db_instance.main.port
}

output "rds_database_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.name
}

output "rds_secret_name" {
  description = "Name of the Kubernetes secret containing RDS credentials"
  value       = kubernetes_secret.rds_credentials.metadata[0].name
}

# CloudFront Outputs
# Remove duplicates with cloudfront.tf
# output "cloudfront_distribution_id" { ... } - Already in cloudfront.tf
# output "cloudfront_domain_name" { ... } - Already in cloudfront.tf

# KMS Outputs
# Remove duplicates with kms-encryption.tf
# output "eks_kms_key_arn" { ... } - Already in kms-encryption.tf
# output "rds_kms_key_arn" { ... } - Already in kms-encryption.tf

# Route53 Outputs
output "route53_zone_id" {
  description = "Route53 zone ID"
  value       = var.route53_zone_id
}

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.cert.arn
}