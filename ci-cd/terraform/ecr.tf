# Continued ECR Configuration

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

# Multiple Repository Creation
resource "aws_ecr_repository" "additional_repos" {
  for_each = toset(var.ecr_repository_names)

  name                 = "${var.project_name}-${each.key}${var.environment == "prod" ? "" : "-${var.environment}"}"
  image_tag_mutability = "IMMUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  encryption_configuration {
    encryption_type = var.ecr_kms_key_arn != "" ? "KMS" : "AES256"
    kms_key         = var.ecr_kms_key_arn != "" ? var.ecr_kms_key_arn : null
  }
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-${each.key}${var.environment == "prod" ? "" : "-${var.environment}"}"
    }
  )
}

# Lifecycle Policy for Additional Repositories
resource "aws_ecr_lifecycle_policy" "additional_repos" {
  for_each = aws_ecr_repository.additional_repos

  repository = each.value.name
  
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
        rulePriority = 3,
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

# Outputs
output "ecr_repository_urls" {
  description = "URLs of the ECR repositories"
  value = merge(
    {
      main = aws_ecr_repository.quantumvestai.repository_url
    },
    var.create_ml_model_repository ? 
      {"ml_models" = aws_ecr_repository.ml_models[0].repository_url} : {},
    {
      for name, repo in aws_ecr_repository.additional_repos : 
      name => repo.repository_url
    }
  )
}

output "ecr_scan_findings_topic_arn" {
  description = "ARN of the SNS topic for ECR scan findings"
  value       = aws_sns_topic.ecr_scan_findings.arn
}

output "ecr_repository_arns" {
  description = "ARNs of the ECR repositories"
  value = merge(
    {
      main = aws_ecr_repository.quantumvestai.arn
    },
    var.create_ml_model_repository ? 
      {"ml_models" = aws_ecr_repository.ml_models[0].arn} : {},
    {
      for name, repo in aws_ecr_repository.additional_repos : 
      name => repo.arn
    }
  )
}