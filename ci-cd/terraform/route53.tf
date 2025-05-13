# Route53 DNS Configuration
# Created: 2025-05-13 20:51:26
# Author: daparthi001

# Application DNS records are defined in their respective files:
# - api.${var.domain_name} defined in loadbalancer.tf
# - cdn.${var.domain_name} defined in cloudfront.tf

# You can add additional DNS records here if needed

# Health check for API endpoint
resource "aws_route53_health_check" "api" {
  fqdn              = "api.${var.domain_name}"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/api/health"
  failure_threshold = 3
  request_interval  = 30
  
  tags = {
    Name = "${var.project}-${var.environment}-api-health"
  }
}

# CloudWatch alarm for API health check
resource "aws_cloudwatch_metric_alarm" "api_health" {
  alarm_name          = "${var.project}-${var.environment}-api-health-alarm"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthCheckStatus"
  namespace           = "AWS/Route53"
  period              = 60
  statistic           = "Minimum"
  threshold           = 1
  alarm_description   = "This alarm monitors the health of the API endpoint"
  
  dimensions = {
    HealthCheckId = aws_route53_health_check.api.id
  }
  
  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
  
  tags = {
    Name = "${var.project}-${var.environment}-api-health-alarm"
  }
}

# SNS topic for alarms
resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.environment}-alerts"
  
  tags = {
    Name = "${var.project}-${var.environment}-alerts"
  }
}