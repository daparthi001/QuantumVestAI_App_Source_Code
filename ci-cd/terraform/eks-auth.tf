# EKS Authentication Configuration

# Remove the duplicate provider "kubernetes" block

# Keep the rest of the file as is
# For example:
resource "kubernetes_config_map" "aws_auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = {
    mapRoles = yamlencode(local.map_roles)
    mapUsers = yamlencode(local.map_users)
  }

  depends_on = [
    aws_eks_cluster.eks
  ]
}

# Keep the rest of your eks-auth.tf content