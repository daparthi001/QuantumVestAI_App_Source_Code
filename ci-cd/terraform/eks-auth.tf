# Kubernetes provider configuration and aws-auth ConfigMap

# Configure the Kubernetes provider to interact with your EKS cluster
provider "kubernetes" {
  host                   = aws_eks_cluster.eks.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.eks.certificate_authority[0].data)
  
  # Use AWS CLI to authenticate to the EKS cluster
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", var.cluster_name, "--region", var.aws_region]
  }
}

# Configure AWS Auth ConfigMap to allow node groups and IAM users to access the cluster
resource "kubernetes_config_map" "aws_auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  # Map IAM roles and users to Kubernetes RBAC
  data = {
    # Map the node role to system:node group
    mapRoles = yamlencode(concat(
      [
        {
          rolearn  = aws_iam_role.eks_node.arn
          username = "system:node:{{EC2PrivateDNSName}}"
          groups   = ["system:bootstrappers", "system:nodes"]
        }
      ],
      # Additional roles from variable, useful for CI/CD roles or other service accounts
      var.additional_iam_roles_for_auth
    ))
    
    # Map specific IAM users to Kubernetes RBAC groups
    mapUsers = yamlencode(concat(
      # Admin user(s)
      var.admin_user_arns != null ? [
        for user_arn in var.admin_user_arns : {
          userarn  = user_arn
          username = "admin:${split("/", user_arn)[1]}"
          groups   = ["system:masters"]
        }
      ] : [],
      
      # Developer user(s) with restricted access
      var.developer_user_arns != null ? [
        for user_arn in var.developer_user_arns : {
          userarn  = user_arn
          username = "dev:${split("/", user_arn)[1]}"
          groups   = ["${var.cluster_name}:developers"]
        }
      ] : [],
      
      # Read-only user(s)
      var.readonly_user_arns != null ? [
        for user_arn in var.readonly_user_arns : {
          userarn  = user_arn
          username = "viewer:${split("/", user_arn)[1]}"
          groups   = ["${var.cluster_name}:readonly"]
        }
      ] : []
    ))
  }

  depends_on = [aws_eks_cluster.eks]
  
  # Add lifecycle policy to prevent Terraform from overwriting manual changes to the ConfigMap
  lifecycle {
    ignore_changes = [
      data["mapAccounts"]
    ]
  }
}

# Create a ClusterRole for developers (limited access)
resource "kubernetes_cluster_role" "developer" {
  count = length(var.developer_user_arns) > 0 ? 1 : 0
  
  metadata {
    name = "${var.cluster_name}:developers"
  }

  # Rules defining what developers can do
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
  
  # Limited to read-only for broader cluster resources
  rule {
    api_groups = [""]
    resources  = ["nodes", "namespaces", "events"]
    verbs      = ["get", "list", "watch"]
  }
}

# Create a ClusterRole for read-only users
resource "kubernetes_cluster_role" "readonly" {
  count = length(var.readonly_user_arns) > 0 ? 1 : 0
  
  metadata {
    name = "${var.cluster_name}:readonly"
  }

  # Rules defining what read-only users can do (only view access)
  rule {
    api_groups = [""]
    resources  = ["*"]
    verbs      = ["get", "list", "watch"]
  }
  
  rule {
    api_groups = ["apps"]
    resources  = ["*"]
    verbs      = ["get", "list", "watch"]
  }
  
  rule {
    api_groups = ["batch"]
    resources  = ["*"]
    verbs      = ["get", "list", "watch"]
  }
  
  rule {
    api_groups = ["autoscaling"]
    resources  = ["*"]
    verbs      = ["get", "list", "watch"]
  }
}

# Create a ClusterRoleBinding for developers
resource "kubernetes_cluster_role_binding" "developer" {
  count = length(var.developer_user_arns) > 0 ? 1 : 0
  
  metadata {
    name = "${var.cluster_name}:developers"
  }
  
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.developer[0].metadata[0].name
  }
  
  # Subjects will be the IAM users mapped via aws-auth ConfigMap
  subject {
    kind      = "Group"
    name      = "${var.cluster_name}:developers"
    api_group = "rbac.authorization.k8s.io"
  }
}

# Create a ClusterRoleBinding for read-only users
resource "kubernetes_cluster_role_binding" "readonly" {
  count = length(var.readonly_user_arns) > 0 ? 1 : 0
  
  metadata {
    name = "${var.cluster_name}:readonly"
  }
  
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.readonly[0].metadata[0].name
  }
  
  # Subjects will be the IAM users mapped via aws-auth ConfigMap
  subject {
    kind      = "Group"
    name      = "${var.cluster_name}:readonly"
    api_group = "rbac.authorization.k8s.io"
  }
}