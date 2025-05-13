# Variables for CloudFront configuration

variable "cdn_domain_name" {
  description = "Domain name for the CloudFront distribution"
  type        = string
  default     = "api.quantumvestai.example.com"
}

variable "cdn_price_class" {
  description = "CloudFront distribution price class"
  type        = string
  default     = "PriceClass_100" # Use PriceClass_All for global distribution
}

variable "cdn_default_ttl" {
  description = "Default TTL for CloudFront cache in seconds"
  type        = number
  default     = 86400 # 1 day
}

variable "cdn_min_ttl" {
  description = "Minimum TTL for CloudFront cache in seconds"
  type        = number
  default     = 0
}

variable "cdn_max_ttl" {
  description = "Maximum TTL for CloudFront cache in seconds"
  type        = number
  default     = 31536000 # 1 year
}

variable "enable_cloudfront_waf" {
  description = "Whether to enable WAF for CloudFront"
  type        = bool
  default     = true
}

variable "cloudfront_waf_rate_limit" {
  description = "Rate limit for CloudFront WAF (requests per 5 minutes)"
  type        = number
  default     = 5000
}

variable "origin_custom_header" {
  description = "Custom header value for CloudFront to ALB communication"
  type        = string
  default     = "some-secret-value" # Change this to a secure random value
}

variable "blocked_countries" {
  description = "List of country codes to block (ISO 3166-1 alpha-2 format)"
  type        = list(string)
  default     = []
}

variable "allowed_countries" {
  description = "List of country codes to allow (ISO 3166-1 alpha-2 format)"
  type        = list(string)
  default     = []
}

variable "cdn_cors_origins" {
  description = "List of allowed origins for CORS"
  type        = list(string)
  default     = ["https://quantumvestai.example.com"]
}

variable "enable_cdn_security_headers" {
  description = "Whether to enable security headers via CloudFront Functions"
  type        = bool
  default     = true
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for the domain"
  type        = string
  default     = ""
}

variable "create_dns_record" {
  description = "Whether to create a DNS record for the CloudFront distribution"
  type        = bool
  default     = false
}

# AWS Provider for us-east-1 region (required for CloudFront certificates)
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}