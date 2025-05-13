# KMS Encryption Keys for QuantumVestAI

# KMS Key for EKS Cluster
resource "aws_kms_key" "eks_key" {
  description             = "KMS key for EKS cluster encryption"
  deletion_window_in_days = var.kms_deletion_window_in_days
  enable_key_rotation     = var.enable_kms_key_rotation
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow EKS service to use the key"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${var.cluster_name}-eks-encryption-key"
    }
  )
}

# KMS Alias for EKS Key
resource "aws_kms_alias" "eks_key_alias" {
  name          = "alias/eks/${var.cluster_name}"
  target_key_id = aws_kms_key.eks_key.key_id
}

# KMS Key for RDS Encryption
resource "aws_kms_key" "rds_key" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = var.kms_deletion_window_in_days
  enable_key_rotation     = var.enable_kms_key_rotation
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow RDS service to use the key"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${var.cluster_name}-rds-encryption-key"
    }
  )
}

# KMS Alias for RDS Key
resource "aws_kms_alias" "rds_key_alias" {
  name          = "alias/rds/${var.cluster_name}"
  target_key_id = aws_kms_key.rds_key.key_id
}

# KMS Key for Secrets Manager
resource "aws_kms_key" "secrets_key" {
  description             = "KMS key for Secrets Manager encryption"
  deletion_window_in_days = var.kms_deletion_window_in_days
  enable_key_rotation     = var.enable_kms_key_rotation
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow Secrets Manager to use the key"
        Effect = "Allow"
        Principal = {
          Service = "secretsmanager.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(
    local.common_tags,
    {
      Name = "${var.cluster_name}-secrets-encryption-key"
    }
  )
}

# KMS Alias for Secrets Manager Key
resource "aws_kms_alias" "secrets_key_alias" {
  name          = "alias/secrets/${var.cluster_name}"
  target_key_id = aws_kms_key.secrets_key.key_id
}

# Outputs
output "eks_kms_key_arn" {
  description = "ARN of the KMS key for EKS encryption"
  value       = aws_kms_key.eks_key.arn
}

output "rds_kms_key_arn" {
  description = "ARN of the KMS key for RDS encryption"
  value       = aws_kms_key.rds_key.arn
}

output "secrets_kms_key_arn" {
  description = "ARN of the KMS key for Secrets Manager encryption"
  value       = aws_kms_key.secrets_key.arn
}