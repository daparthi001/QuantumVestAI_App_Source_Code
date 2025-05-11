
output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "vpc_id" {
  value = aws_vpc.main.id
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
