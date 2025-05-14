# CloudFront Configuration
# Updated: 2025-05-14 00:14:04
# Author: daparthi001

# ACM Certificate for CloudFront (must be in us-east-1)
resource "aws_acm_certificate" "cloudfront" {
  provider          = aws.us_east_1
  domain_name       = "cdn.${var.domain_name}"  
  subject_alternative_names = ["*.cdn.${var.domain_name}"]
  validation_method = "DNS"
  
  lifecycle {
    create_before_destroy = true
  }
}

# CloudFront Origin Access Identity
resource "aws_cloudfront_origin_access_identity" "frontend_oai" {
  comment = "OAI for ${var.project}-${var.environment} frontend"
}

# CloudFront distribution for frontend assets
resource "aws_cloudfront_distribution" "frontend" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "${var.project}-${var.environment} Frontend"
  default_root_object = "index.html"
  price_class         = var.cloudfront_price_class
  
  # S3 origin for static assets
  origin {
    domain_name = aws_s3_bucket.frontend_assets.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.frontend_assets.bucket}"
    
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.frontend_oai.cloudfront_access_identity_path
    }
  }
  
  # API origin for dynamic content
  origin {
    domain_name = aws_lb.main.dns_name
    origin_id   = "ALB-${aws_lb.main.name}"
    
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }
  
  # Default behavior for S3 assets
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend_assets.bucket}"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }
  
  # API behavior for backend
  ordered_cache_behavior {
    path_pattern     = "/api/*"
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB-${aws_lb.main.name}"
    
    forwarded_values {
      query_string = true
      headers      = ["Authorization", "Host"]
      cookies {
        forward = "all"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
  }
  
  # SPA support - direct all routes to index.html except for files with extensions
  ordered_cache_behavior {
    path_pattern     = "/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.frontend_assets.bucket}"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    
    lambda_function_association {
      event_type   = "origin-request"
      include_body = false
      lambda_arn   = aws_lambda_function.spa_router.qualified_arn
    }
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
  
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  
  aliases = ["cdn.${var.domain_name}"]
  
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.cloudfront.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}

# CloudFront Function for SPA routing
resource "aws_iam_role" "lambda_edge_role" {
  name = "${var.project}-${var.environment}-lambda-edge-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["lambda.amazonaws.com", "edgelambda.amazonaws.com"]
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_edge_policy" {
  name        = "${var.project}-${var.environment}-lambda-edge-policy"
  description = "Policy for Lambda@Edge SPA router function"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_edge_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_edge_policy.arn
  role       = aws_iam_role.lambda_edge_role.name
}

# Create a zip file for the Lambda function
data "archive_file" "spa_router" {
  type        = "zip"
  output_path = "${path.module}/spa_router.zip"
  
  source {
    content  = <<-EOT
      // SPA router for CloudFront
      exports.handler = (event, context, callback) => {
        const request = event.Records[0].cf.request;
        const uri = request.uri;
        
        // Check if the request is for a file with an extension
        if (uri.includes('.')) {
          callback(null, request);
          return;
        }
        
        // Otherwise, rewrite to index.html
        request.uri = '/index.html';
        callback(null, request);
      };
    EOT
    filename = "index.js"
  }
}

resource "aws_lambda_function" "spa_router" {
  provider         = aws.us_east_1
  filename         = data.archive_file.spa_router.output_path
  function_name    = "${var.project}-${var.environment}-spa-router"
  role             = aws_iam_role.lambda_edge_role.arn
  handler          = "index.handler"
  source_code_hash = data.archive_file.spa_router.output_base64sha256
  runtime          = "nodejs16.x"
  publish          = true
}

# Route53 record for CloudFront
resource "aws_route53_record" "cdn" {
  zone_id = var.route53_zone_id
  name    = "cdn.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}