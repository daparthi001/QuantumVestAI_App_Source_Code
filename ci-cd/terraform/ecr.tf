# ECR Repository Configuration for QuantumVestAI

# Main ECR Repository
resource "aws_ecr_repository" "quantumvestai" {
  name                 = "${var.project_name}${var.environment == "prod" ? "" : "-${var.environment}"}"
  image_tag_mutability = "IMMUTABLE"  # Best practice for security: prevent tag overwrites
  
  # Enable image scanning on push
  image_scanning_configuration {
    scan_on_push = true
  }
  
  # Enable encryption with KMS
  encryption_configuration {
    encryption_type = var.ecr_kms_key_arn != "" ? "KMS" : "AES256"
    kms_key         = var.ecr_kms_key_arn != "" ? var.ecr_kms_key_arn : null
  }
  
  # Tags
  tags = merge(
    local.tags,
    {
      Name = "${var.project_name}${var.environment == "prod" ? "" : "-${var.environment}"}"
    }
  )
}

# Repository Policy (allows cross-account access if needed)
resource "aws_ecr_repository_policy" "quantumvestai" {
  count      = length(var.ecr_repository_account_ids) > 0 ? 1 : 0
  repository = aws_ecr_repository.quantumvestai.name
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "AllowCrossAccountAccess",
        Effect = "Allow",
        Principal = {
          AWS = formatlist("arn:aws:iam::%s:root", var.ecr_repository_account_ids)
        },
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
      }
    ]
  })
}

# Lifecycle Policy (to manage image retention)
resource "aws_ecr_lifecycle_policy" "quantumvestai" {
  repository = aws_ecr_repository.quantumvestai.name
  
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep only the last ${var.ecr_image_count_main} images with 'latest' tag",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["latest"],
          countType     = "imageCountMoreThan",
          countNumber   = var.ecr_image_count_main
        },
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2,
        description  = "Keep only the last ${var.ecr_image_count_feature} images with feature branch tags",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["feature-"],
          countType     = "imageCountMoreThan",
          countNumber   = var.ecr_image_count_feature
        },
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 3,
        description  = "Keep last ${var.ecr_image_count_prod} production images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["prod-", "release-"],
          countType     = "imageCountMoreThan",
          countNumber   = var.ecr_image_count_prod
        },
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 4,
        description  = "Remove untagged images after ${var.ecr_untagged_image_days} days",
        selection = {
          tagStatus   = "untagged",
          countType   = "sinceImagePushed",
          countUnit   = "days",
          countNumber = var.ecr_untagged_image_days
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ML Model Images Repository (separate repository for model training images)
resource "aws_ecr_repository" "ml_models" {
  count                = var.create_ml_model_repository ? 1 : 0
  name                 = "${var.project_name}-ml-models${var.environment == "prod" ? "" : "-${var.environment}"}"
  image_tag_mutability = "IMMUTABLE"
  
  # Enable image scanning on push
  image_scanning_configuration {
    scan_on_push = true
  }
  
  # Enable encryption with KMS
  encryption_configuration {
    encryption_type = var.ecr_kms_key_arn != "" ? "KMS" : "AES256"
    kms_key         = var.ecr_kms_key_arn != "" ? var.ecr_kms_key_arn : null
  }
  
  # Tags
  tags = merge(
    local.tags,
    {
      Name = "${var.project_name}-ml-models${var.environment == "prod" ? "" : "-${var.environment}"}"
    }
  )
}

# Lifecycle Policy for ML Model Images
resource "aws_ecr_lifecycle_policy" "ml_models" {
  count      = var.create_ml_model_repository ? 1 : 0
  repository = aws_ecr_repository.ml_models[0].name
  
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1,
        description  = "Keep only the last ${var.ecr_ml_model_count} released model images",
        selection = {
          tagStatus     = "tagged",
          tagPrefixList = ["release-", "model-"],
          countType     = "imageCountMoreThan",
          countNumber   = var.ecr_ml_model_count
        },
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2,
        description  = "Remove untagged images after ${var.ecr_untagged_image_days} days",
        selection = {
          tagStatus   = "untagged",
          countType   = "sinceImagePushed",
          countUnit   = "days",
          countNumber = var.ecr_untagged_image_days
        },
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# CloudWatch Event Rule to send notifications for ECR image scan findings
resource "aws_cloudwatch_event_rule" "ecr_scan_findings" {
  name        = "${var.project_name}-ecr-scan-findings-${var.environment}"
  description = "Event rule for ECR image scan findings"
  
  event_pattern = jsonencode({
    source      = ["aws.ecr"],
    detail-type = ["ECR Image Scan"],
    detail = {
      repository-name = [
        aws_ecr_repository.quantumvestai.name,
        var.create_ml_model_repository ? aws_ecr_repository.ml_models[0].name : ""
      ],
      finding-severity-counts = {
        CRITICAL = [{ exists = true }],
        HIGH     = [{ exists = true }]
      }
    }
  })
  
  tags = local.tags
}

# CloudWatch Event Target for ECR scan findings
resource "aws_cloudwatch_event_target" "ecr_scan_findings" {
  rule      = aws_cloudwatch_event_rule.ecr_scan_findings.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.ecr_scan_findings.arn
}

# SNS Topic for ECR scan findings
resource "aws_sns_topic" "ecr_scan_findings" {
  name = "${var.project_name}-ecr-scan-findings-${var.environment}"
  
  tags = local.tags
}

# SNS Topic Policy
resource "aws_sns_topic_policy" "ecr_scan_findings" {
  arn    = aws_sns_topic.ecr_scan_findings.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

# IAM Policy Document for SNS Topic
data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]
    
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    
    resources = [aws_sns_topic.ecr_scan_findings.arn]
  }
}

# SNS Topic Subscription (if an email is provided)
resource "aws_sns_topic_subscription" "ecr_scan_findings" {
  count     = var.ecr_scan_notification_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.ecr_scan_findings.arn
  protocol  = "email"
  endpoint  = var.ecr_scan_notification_email
}

# Output values
output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.quantumvestai.repository_url
}

output "ml_models_repository_url" {
  description = "URL of the ML models ECR repository"
  value       = var.create_ml_model_repository ? aws_ecr_repository.ml_models[0].repository_url : null
}

output "ecr_scan_findings_topic_arn" {
  description = "ARN of the SNS topic for ECR scan findings"
  value       = aws_sns_topic.ecr_scan_findings.arn
}