resource "aws_route53_record" "app" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "quantumvestai.com"
  type    = "A"

  alias {
    name                   = aws_lb.app.dns_name
    zone_id                = aws_lb.app.zone_id
    evaluate_target_health = true
  }
}


