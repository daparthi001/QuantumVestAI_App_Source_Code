# EKS Authentication Configuration

# AWS Auth ConfigMap for RBAC
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

# RBAC for developers
resource "kubernetes_cluster_role" "developer" {
  metadata {
    name = "${var.cluster_name}-developer"
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps", "secrets", "persistentvolumeclaims"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }

  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "statefulsets", "daemonsets", "replicasets"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }

  rule {
    api_groups = ["batch"]
    resources  = ["jobs", "cronjobs"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }

  rule {
    api_groups = ["networking.k8s.io"]
    resources  = ["ingresses"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }

  depends_on = [aws_eks_cluster.eks]
}

resource "kubernetes_cluster_role_binding" "developer" {
  metadata {
    name = "${var.cluster_name}-developer-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.developer.metadata[0].name
  }
  subject {
    kind      = "Group"
    name      = "${var.cluster_name}-developers"
    api_group = "rbac.authorization.k8s.io"
  }

  depends_on = [kubernetes_cluster_role.developer]
}

# RBAC for read-only users
resource "kubernetes_cluster_role" "readonly" {
  metadata {
    name = "${var.cluster_name}-readonly"
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps", "secrets", "persistentvolumeclaims", "namespaces"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "statefulsets", "daemonsets", "replicasets"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["batch"]
    resources  = ["jobs", "cronjobs"]
    verbs      = ["get", "list", "watch"]
  }

  rule {
    api_groups = ["networking.k8s.io"]
    resources  = ["ingresses"]
    verbs      = ["get", "list", "watch"]
  }

  depends_on = [aws_eks_cluster.eks]
}

resource "kubernetes_cluster_role_binding" "readonly" {
  metadata {
    name = "${var.cluster_name}-readonly-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.readonly.metadata[0].name
  }
  subject {
    kind      = "Group"
    name      = "${var.cluster_name}-readonly"
    api_group = "rbac.authorization.k8s.io"
  }

  depends_on = [kubernetes_cluster_role.readonly]
}

# Create namespaces for each environment
resource "kubernetes_namespace" "environments" {
  for_each = toset(var.environments)
  
  metadata {
    name = each.value
    
    labels = {
      name = each.value
      environment = each.value
    }
  }

  depends_on = [aws_eks_cluster.eks]
}