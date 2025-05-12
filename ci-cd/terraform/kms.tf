resource "aws_kms_alias" "this" {
  name          = "alias/eks/quantumvestai-eks"
  target_key_id = aws_kms_key.this.key_id
}
