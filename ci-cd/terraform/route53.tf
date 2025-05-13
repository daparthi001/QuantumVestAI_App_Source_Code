# Route53 Configuration

# Keep main Route53 configurations

# Remove these duplicate resources:
# resource "aws_route53_record" "app" { ... }
# resource "aws_route53_record" "cdn" { ... }

# Remove duplicate outputs:
# output "route53_zone_id" { ... }
# output "acm_certificate_arn" { ... }

# Keep the rest of your Route53 configuration