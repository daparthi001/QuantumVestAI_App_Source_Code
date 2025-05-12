output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "route53_zone_id" {
  value = aws_route53_zone.main.zone_id
}

output "acm_certificate_arn" {
  value = aws_acm_certificate.cert.arn
}
