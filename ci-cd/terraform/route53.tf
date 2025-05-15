# If you already have a hosted zone, use this instead
data "aws_route53_zone" "existing" {
  name = "quantumvestai.com"
  private_zone = false
}

# A record for root domain with alias to ALB
resource "aws_route53_record" "root" {
  zone_id = data.aws_route53_zone.existing.zone_id
  name    = "quantumvestai.com"
  type    = "A"

  alias {
    name                   = "k8s-quantumvestai-4c2477a64e-1686495198.us-east-1.elb.amazonaws.com"
    zone_id                = "Z35SXDOTRQ7X7K"
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.existing.zone_id
  name    = "www.quantumvestai.com"
  type    = "CNAME"
  ttl     = 300
  records = ["k8s-quantumvestai-4c2477a64e-1686495198.us-east-1.elb.amazonaws.com"]
}