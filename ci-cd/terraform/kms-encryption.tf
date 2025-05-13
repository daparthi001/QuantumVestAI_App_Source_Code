# KMS Encryption for EKS and related services

# KMS Key for EKS cluster encryption
resource "aws_kms_key" "eks_key" {
  description             = "KMS key for QuantumVestAI EKS cluster encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  # Add a key policy to allow EKS service to use this key
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid = "Enable IAM User Permissions",
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        Action = "kms:*",
        Resource = "*"
      },
      {
        Sid = "Allow EKS service to use the key",
        Effect = "Allow",
        Principal = {
          Service = "eks.amazonaws.com"
        },
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ],
        Resource = "*"
      }
    ]
  })
  
  tags = merge(
    local.tags,
    {
      Name = "${var.cluster_name}-eks-encryption-key"
    }
  )
}

# KMS Alias for EKS key
resource "aws_kms_alias" "eks_key_alias" {
  name          = "alias/eks/${var.cluster_name}"
  target_key_id = aws_kms_key.eks_key.key_id
}

# KMS Key for RDS encryption
resource "aws_kms_key" "rds_key" {
  description             = "KMS key for QuantumVestAI RDS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  # Add a key policy to allow RDS service to use this key
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid = "Enable IAM User Permissions",
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        Action = "kms:*",
        Resource = "*"
      },
      {
        Sid = "Allow RDS service to use the key",
        Effect = "Allow",
        Principal = {
          Service = "rds.amazonaws.com"
        },
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ],
        Resource = "*"
      }
    ]
  })
  
  tags = merge(
    local.tags,
    {
      Name = "${var.cluster_name}-rds-encryption-key"
    }
  )
}

# KMS Alias for RDS key
resource "aws_kms_alias" "rds_key_alias" {
  name          = "alias/rds/${var.cluster_name}"
  target_key_id = aws_kms_key.rds_key.key_id
}

# KMS Key for Secrets Manager
resource "aws_kms_key" "secrets_key" {
  description             = "KMS key for QuantumVestAI Secrets Manager encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  # Add a key policy to allow Secrets Manager service to use this key
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid = "Enable IAM User Permissions",
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        Action = "kms:*",
        Resource = "*"
      },
      {
        Sid = "Allow Secrets Manager service to use the key",
        Effect = "Allow",
        Principal = {
          Service = "secretsmanager.amazonaws.com"
        },
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ],
        Resource = "*"
      }
    ]
  })
  
  tags = merge(
    local.tags,
    {
      Name = "${var.cluster_name}-secrets-encryption-key"
    }
  )
}

# KMS Alias for Secrets Manager key
resource "aws_kms_alias" "secrets_key_alias" {
  name          = "alias/secretsmanager/${var.cluster_name}"
  target_key_id = aws_kms_key.secrets_key.key_id
}

# Get the current AWS account ID
data "aws_caller_identity" "current1" {}

# Update the EKS cluster to use KMS encryption
resource "aws_eks_cluster" "eks_kms" {
  # Other configuration remains the same
  
  # Add encryption configuration
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_key.arn
    }
    resources = ["secrets"]
  }
  
  # ...existing configuration continues
}

# Update RDS instance to use KMS encryption
resource "aws_db_instance" "quantumvestai-kms" {
  # Other configuration remains the same
  
  # Add KMS key for storage encryption
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds_key.arn
  
  # ...existing configuration continues
}

# Update Secrets Manager secret to use KMS encryption
resource "aws_secretsmanager_secret" "rds_credentials-kms" {
  # Other configuration remains the same
  
  # Add KMS key for secrets encryption
  kms_key_id = aws_kms_key.secrets_key.arn
  
  # ...existing configuration continues
}

# Add outputs for KMS keys
output "eks_kms_key_arn" {
  description = "ARN of KMS key used for EKS encryption"
  value       = aws_kms_key.eks_key.arn
}

output "rds_kms_key_arn" {
  description = "ARN of KMS key used for RDS encryption"
  value       = aws_kms_key.rds_key.arn
}

output "secrets_kms_key_arn" {
  description = "ARN of KMS key used for Secrets Manager encryption"
  value       = aws_kms_key.secrets_key.arn
}