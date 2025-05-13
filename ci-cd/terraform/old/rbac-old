resource "kubernetes_role" "readonly" {
  metadata {
    name      = "readonly"
    namespace = "default"
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding" "readonly_binding" {
  metadata {
    name      = "readonly-binding"
    namespace = "default"
  }

  subject {
    kind      = "User"
    name      = "k8s-user"
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    kind      = "Role"
    name      = "readonly"
    api_group = "rbac.authorization.k8s.io"
  }
}