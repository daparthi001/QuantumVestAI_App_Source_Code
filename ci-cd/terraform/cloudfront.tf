# CloudFront Distribution for QuantumVestAI API

# CloudFront origin request policy
resource "aws_cloudfront_origin_request_policy" "api_policy" {
  name    = "${var.project_name}-api-policy-${var.environment}"
  comment = "QuantumVestAI API origin request policy"
  
  cookies_config {
    cookie_behavior = "none"
  }
  
  headers_config {
    header_behavior = "whitelist"
    headers {
      items = ["Host", "Origin", "Authorization", "Accept", "Content-Type"]
    }
  }
  
  query_strings_config {
    query_string_behavior = "all"
  }
}

# CloudFront cache policy
resource "aws_cloudfront_cache_policy" "api_cache_policy" {
  name        = "${var.project_name}-api-cache-policy-${var.environment}"
  comment     = "QuantumVestAI API cache policy"
  default_ttl = var.cdn_default_ttl
  max_ttl     = var.cdn_max_ttl
  min_ttl     = var.cdn_min_ttl
  
  parameters_in_cache_key_and_forwarded_to_origin {
    cookies_config {
      cookie_behavior = "none"
    }
    
    headers_config {
      header_behavior = "whitelist"
      headers {
        items = ["Authorization", "Accept", "Content-Type"]
      }
    }
    
    query_strings_config {
      query_string_behavior = "whitelist"
      query_strings {
        items = ["ticker", "model", "days", "format"]
      }
    }
    
    enable_accept_encoding_brotli = true
    enable_accept_encoding_gzip   = true
  }
}

# CloudFront response headers policy
resource "aws_cloudfront_response_headers_policy" "security_headers" {
  name    = "${var.project_name}-security-headers-${var.environment}"
  comment = "Security headers policy for QuantumVestAI API"
  
  security_headers_config {
    content_type_options {
      override = true
    }
    
    frame_options {
      frame_option = "DENY"
      override     = true
    }
    
    referrer_policy {
      referrer_policy = "same-origin"
      override        = true
    }
    
    strict_transport_security {
      access_control_max_age_sec = 63072000 # 2 years
      include_subdomains         = true
      override                   = true
      preload                    = true
    }
    
    xss_protection {
      mode_block = true
      protection = true
      override   = true
    }
  }
  
  cors_config {
    access_control_allow_credentials = false
    
    access_control_allow_headers {
      items = ["Authorization", "Content-Type", "Accept"]
    }
    
    access_control_allow_methods {
      items = ["GET", "HEAD", "OPTIONS", "POST", "PUT", "DELETE"]
    }
    
    access_control_allow_origins {
      items = var.cdn_cors_origins
    }
    
    origin_override = true
  }
}

# WAF Web ACL for CloudFront
resource "aws_wafv2_web_acl" "cloudfront_waf" {
  count = var.enable_cloudfront_waf ? 1 : 0
  
  name        = "${var.project_name}-cloudfront-waf-${var.environment}"
  description = "WAF for QuantumVestAI CloudFront distribution"
  scope       = "CLOUDFRONT"

  default_action {
    allow {}
  }

  # AWS Managed Core Rule Set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 10

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # AWS Managed SQL Injection Rule Set
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 20

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }
  
  # Rate-based rule to prevent DDoS
  rule {
    name     = "RateLimitRule"
    priority = 30

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.cloudfront_waf_rate_limit
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

  # Geo-blocking rule (optional)
  dynamic "rule" {
    for_each = length(var.blocked_countries) > 0 ? [1] : []
    
    content {
      name     = "GeoBlockRule"
      priority = 40

      action {
        block {}
      }

      statement {
        geo_match_statement {
          country_codes = var.blocked_countries
        }
      }

      visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "GeoBlockRule"
        sampled_requests_enabled   = true
      }
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project_name}-cloudfront-waf-${var.environment}"
    sampled_requests_enabled   = true
  }

  tags = local.tags
}

# ACM Certificate for CloudFront (in us-east-1 region)
resource "aws_acm_certificate" "cdn" {
  provider = aws.us_east_1
  
  domain_name       = var.cdn_domain_name
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

# CloudFront distribution
resource "aws_cloudfront_distribution" "api_cdn" {
  origin {
    domain_name = aws_lb.app.dns_name
    origin_id   = "eks-api-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
    
    # Custom headers for origin security
    custom_header {
      name  = "X-Origin-Verify"
      value = var.origin_custom_header
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CDN for QuantumVestAI API - ${var.environment}"
  default_root_object = ""
  price_class         = var.cdn_price_class
  web_acl_id          = var.enable_cloudfront_waf ? aws_wafv2_web_acl.cloudfront_waf[0].arn : null
  
  # Logging configuration
  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cdn_logs.bucket_domain_name
    prefix          = "cdn-logs"
  }

  # Default cache behavior
  default_cache_behavior {
    target_origin_id       = "eks-api-origin"
    viewer_protocol_policy = "redirect-to-https"
    
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    compress         = true
    
    # Use the cache policy and origin request policy
    cache_policy_id          = aws_cloudfront_cache_policy.api_cache_policy.id
    origin_request_policy_id = aws_cloudfront_origin_request_policy.api_policy.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security_headers.id
    
    # Function associations
    dynamic "function_association" {
      for_each = var.enable_cdn_security_headers ? [1] : []
      
      content {
        event_type   = "viewer-response"
        function_arn = aws_cloudfront_function.security_headers[0].arn
      }
    }
  }
  
  # Cache behavior for static assets (if applicable)
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "eks-api-origin"
    
    cache_policy_id            = aws_cloudfront_cache_policy.api_cache_policy.id
    origin_request_policy_id   = aws_cloudfront_origin_request_policy.api_policy.id
    response_headers_policy_id = aws_cloudfront_response_headers_policy.security_headers.id
    
    compress               = true
    viewer_protocol_policy = "redirect-to-https"
  }

  # Geo restriction
  restrictions {
    geo_restriction {
      restriction_type = length(var.blocked_countries) > 0 ? "whitelist" : "none"
      locations        = length(var.blocked_countries) > 0 ? var.allowed_countries : []
    }
  }

  # SSL/TLS configuration
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.cdn.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
  
  # Custom error responses
  custom_error_response {
    error_code            = 403
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }
  
  custom_error_response {
    error_code            = 404
    response_code         = 200
    response_page_path    = "/index.html"
    error_caching_min_ttl = 10
  }

  tags = local.tags
}

# CloudFront function for security headers (simple edge functions)
resource "aws_cloudfront_function" "security_headers" {
  count = var.enable_cdn_security_headers ? 1 : 0
  
  name    = "${var.project_name}-security-headers-${var.environment}"
  runtime = "cloudfront-js-1.0"
  comment = "Add security headers to responses"
  publish = true
  code    = <<-EOT
    function handler(event) {
      var response = event.response;
      var headers = response.headers;
      
      // Set security headers
      headers['strict-transport-security'] = { value: 'max-age=63072000; includeSubdomains; preload' };
      headers['content-security-policy'] = { value: "default-src 'self'; img-src 'self'; script-src 'self'; style-src 'self'; font-src 'self'; frame-ancestors 'none'" };
      headers['x-content-type-options'] = { value: 'nosniff' };
      headers['x-frame-options'] = { value: 'DENY' };
      headers['x-xss-protection'] = { value: '1; mode=block' };
      headers['referrer-policy'] = { value: 'same-origin' };
      
      return response;
    }
  EOT
}

# S3 bucket for CloudFront logs
resource "aws_s3_bucket" "cdn_logs" {
  bucket = "${var.project_name}-cdn-logs-${var.environment}-${random_string.cdn_suffix.result}"
  
  force_destroy = var.environment != "prod"

  tags = local.tags
}

# Random string for S3 bucket name uniqueness
resource "aws_s3_bucket_policy" "cdn_logs" {
  bucket = aws_s3_bucket.cdn_logs.id
  policy = data.aws_iam_policy_document.cdn_logs.json
}

# Policy document for CloudFront logs
data "aws_iam_policy_document" "cdn_logs" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    actions = [
      "s3:PutObject"
    ]
    resources = [
      "${aws_s3_bucket.cdn_logs.arn}/*"
    ]
    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = [aws_cloudfront_distribution.api_cdn.arn]
    }
  }
}

# Random string for S3 bucket name uniqueness
resource "random_string" "cdn_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Route53 record for custom domain
resource "aws_route53_record" "cdn" {
  count = var.create_dns_record ? 1 : 0
  
  zone_id = var.route53_zone_id
  name    = var.cdn_domain_name
  type    = "A"
  
  alias {
    name                   = aws_cloudfront_distribution.api_cdn.domain_name
    zone_id                = aws_cloudfront_distribution.api_cdn.hosted_zone_id
    evaluate_target_health = false
  }
}

# CloudWatch Alarm for CloudFront 5XX errors
resource "aws_cloudwatch_metric_alarm" "cloudfront_5xx" {
  alarm_name          = "${var.project_name}-cloudfront-5xx-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "5xxErrorRate"
  namespace           = "AWS/CloudFront"
  period              = "60"
  statistic           = "Average"
  threshold           = "5"
  alarm_description   = "This alarm monitors CloudFront 5XX error rate"
  alarm_actions       = [aws_sns_topic.alb_alerts.arn]
  ok_actions          = [aws_sns_topic.alb_alerts.arn]
  
  dimensions = {
    DistributionId = aws_cloudfront_distribution.api_cdn.id
    Region         = "Global"
  }

  tags = local.tags
}

# Outputs
output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.api_cdn.id
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.api_cdn.domain_name
}

output "cloudfront_hosted_zone_id" {
  description = "Hosted zone ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.api_cdn.hosted_zone_id
}