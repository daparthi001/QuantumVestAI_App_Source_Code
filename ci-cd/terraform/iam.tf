# IAM Roles and Policies (Additional to EKS roles)

# Custom policy for S3 access (for ML model storage)
resource "aws_iam_policy" "s3_model_access" {
  name        = "${var.cluster_name}-s3-model-access"
  description = "Policy for accessing S3 buckets for ML model storage"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::${var.model_storage_bucket}",
          "arn:aws:s3:::${var.model_storage_bucket}/*"
        ]
      }
    ]
  })

  
}

# Attach S3 access policy to node role
resource "aws_iam_role_policy_attachment" "s3_model_access" {
  policy_arn = aws_iam_policy.s3_model_access.arn
  role       = aws_iam_role.eks_node.name
}

# Additional CloudWatch policy for logs
resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
  role       = aws_iam_role.eks_node.name
}