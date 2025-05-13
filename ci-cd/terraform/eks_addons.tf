# EKS add-ons configuration

# Install EKS add-ons
resource "aws_eks_addon" "vpc_cni" {
  cluster_name = aws_eks_cluster.eks.name
  addon_name   = "vpc-cni"
  addon_version = var.eks_addon_versions["vpc_cni"]

  resolve_conflicts_on_update = "OVERWRITE"

  tags = local.tags
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name = aws_eks_cluster.eks.name
  addon_name   = "kube-proxy"
  addon_version = var.eks_addon_versions["kube_proxy"]

  resolve_conflicts_on_update = "OVERWRITE"

  tags = local.tags
}

resource "aws_eks_addon" "coredns" {
  cluster_name = aws_eks_cluster.eks.name
  addon_name   = "coredns"
  addon_version = var.eks_addon_versions["coredns"]

  resolve_conflicts_on_update = "OVERWRITE"

  tags = local.tags
}

resource "aws_eks_addon" "aws_ebs_csi_driver" {
  cluster_name = aws_eks_cluster.eks.name
  addon_name   = "aws-ebs-csi-driver"
  addon_version = var.eks_addon_versions["aws_ebs_csi_driver"]

  resolve_conflicts_on_update = "OVERWRITE"

  # EBS CSI driver needs IAM permissions to create volumes
  service_account_role_arn = aws_iam_role.ebs_csi_driver.arn

  tags = local.tags
}

# Create IAM role for EBS CSI driver
resource "aws_iam_role" "ebs_csi_driver" {
  name = "${var.cluster_name}-ebs-csi-driver"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.eks.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(aws_eks_cluster.eks.identity[0].oidc[0].issuer, "https://", "")}:sub": "system:serviceaccount:kube-system:ebs-csi-controller-sa"
          }
        }
      }
    ]
  })

  tags = local.tags
}

# Attach policy for EBS CSI driver
resource "aws_iam_role_policy_attachment" "ebs_csi_driver" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
  role       = aws_iam_role.ebs_csi_driver.name
}

# Create outputs
output "eks_addons" {
  description = "Installed EKS addons"
  value = {
    vpc_cni = aws_eks_addon.vpc_cni.id
    kube_proxy = aws_eks_addon.kube_proxy.id
    coredns = aws_eks_addon.coredns.id
    aws_ebs_csi_driver = aws_eks_addon.aws_ebs_csi_driver.id
  }
}
