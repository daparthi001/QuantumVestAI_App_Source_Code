# Route53 Configuration for QuantumVestAI

# Route53 Hosted Zone (if not already existing)
resource "aws_route53_zone" "main" {
  count = var.route53_zone_id == "" ? 1 : 0
  name  = var.domain_name
}

# ACM Certificate
resource "aws_acm_certificate" "cert" {
  provider = aws.us_east_1

  domain_name       = var.domain_name
  validation_method = "DNS"

  subject_alternative_names = [
    "*.${var.domain_name}"
  ]

  lifecycle {
    create_before_destroy = true
  }

  tags = local.common_tags
}

# DNS Validation Records
resource "aws_route53_record" "validation" {
  for_each = {
    for dvo in aws_acm_certificate.cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id = var.route53_zone_id != "" ? var.route53_zone_id : aws_route53_zone.main[0].zone_id
  name    = each.value.name
  type    = each.value.type
  records = [each.value.record]
  ttl     = 60
}

# Certificate Validation
resource "aws_acm_certificate_validation" "cert" {
  provider = aws.us_east_1

  certificate_arn         = aws_acm_certificate.cert.arn
  validation_record_fqdns = [for record in aws_route53_record.validation : record.fqdn]
}

# Route53 Record for Load Balancer
resource "aws_route53_record" "app" {
  zone_id = var.route53_zone_id != "" ? var.route53_zone_id : aws_route53_zone.main[0].zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}

# CloudFront Route53 Record
resource "aws_route53_record" "cdn" {
  count = var.create_dns_record ? 1 : 0
  
  zone_id = var.route53_zone_id != "" ? var.route53_zone_id : aws_route53_zone.main[0].zone_id
  name    = var.cdn_domain_name
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.api_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.api_cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

# Outputs
output "route53_zone_id" {
  description = "Route53 Hosted Zone ID"
  value       = var.route53_zone_id != "" ? var.route53_zone_id : aws_route53_zone.main[0].zone_id
}

output "acm_certificate_arn" {
  description = "ARN of the ACM certificate"
  value       = aws_acm_certificate.cert.arn
}