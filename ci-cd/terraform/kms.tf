resource "aws_kms_key" "eks_key" {
  description             = "KMS key for QuantumVestAI EKS cluster"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_kms_alias" "eks_key_alias" {
  name          = "alias/eks/quantumvestai-eks2"
  target_key_id = aws_kms_key.eks_key.key_id
}
