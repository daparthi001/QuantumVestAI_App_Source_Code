# Kubernetes RBAC Configuration for QuantumVestAI

# Create namespaces for different environments
resource "kubernetes_namespace" "quantumvestai-rbac" {
  for_each = toset(var.environments)
  
  metadata {
    name = "quantumvestai-${each.key}"
    
    labels = {
      app         = "quantumvestai"
      environment = each.key
      managed-by  = "terraform"
    }
  }
}

# Read-only Role for application namespaces
resource "kubernetes_role" "readonly" {
  for_each = toset(var.environments)
  
  metadata {
    name      = "readonly"
    namespace = kubernetes_namespace.quantumvestai[each.key].metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "services", "configmaps", "secrets", "persistentvolumeclaims", "events"]
    verbs      = ["get", "list", "watch"]
  }
  
  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "statefulsets", "replicasets"]
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
}

# Developer Role (more permissions)
resource "kubernetes_role" "developer" {
  for_each = toset(var.environments)
  
  metadata {
    name      = "developer"
    namespace = kubernetes_namespace.quantumvestai[each.key].metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "pods/log", "pods/exec", "services", "configmaps", "secrets", "persistentvolumeclaims"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  
  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "statefulsets", "replicasets"]
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
  
  # View-only access to events for troubleshooting
  rule {
    api_groups = [""]
    resources  = ["events"]
    verbs      = ["get", "list", "watch"]
  }
}

# ML Engineer Role (specific permissions for ML workloads)
resource "kubernetes_role" "ml_engineer" {
  for_each = toset(var.environments)
  
  metadata {
    name      = "ml-engineer"
    namespace = kubernetes_namespace.quantumvestai[each.key].metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "pods/log", "pods/exec", "services", "configmaps", "persistentvolumeclaims"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  
  rule {
    api_groups = ["batch"]
    resources  = ["jobs", "cronjobs"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  
  # Limited access to deployments (only for model serving)
  rule {
    api_groups = ["apps"]
    resources  = ["deployments"]
    verbs      = ["get", "list", "watch", "create", "update", "patch"]
  }
  
  # Read-only access to secrets
  rule {
    api_groups = [""]
    resources  = ["secrets"]
    verbs      = ["get", "list", "watch"]
  }
  
  # View-only access to events for troubleshooting
  rule {
    api_groups = [""]
    resources  = ["events"]
    verbs      = ["get", "list", "watch"]
  }
}

# Admin Role (full permissions in namespace)
resource "kubernetes_role" "admin" {
  for_each = toset(var.environments)
  
  metadata {
    name      = "admin"
    namespace = kubernetes_namespace.quantumvestai[each.key].metadata[0].name
  }

  rule {
    api_groups = ["*"]
    resources  = ["*"]
    verbs      = ["*"]
  }
}

# RoleBindings for read-only users
resource "kubernetes_role_binding" "readonly_binding" {
  for_each = {
    for binding in local.role_bindings : "${binding.environment}-${binding.username}" => binding
    if binding.role == "readonly"
  }
  
  metadata {
    name      = "readonly-${each.value.username}"
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
  }

  subject {
    kind      = "User"
    name      = each.value.username
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    kind      = "Role"
    name      = kubernetes_role.readonly[each.value.environment].metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }
}

# RoleBindings for developers
resource "kubernetes_role_binding" "developer_binding" {
  for_each = {
    for binding in local.role_bindings : "${binding.environment}-${binding.username}" => binding
    if binding.role == "developer"
  }
  
  metadata {
    name      = "developer-${each.value.username}"
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
  }

  subject {
    kind      = "User"
    name      = each.value.username
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    kind      = "Role"
    name      = kubernetes_role.developer[each.value.environment].metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }
}

# RoleBindings for ML engineers
resource "kubernetes_role_binding" "ml_engineer_binding" {
  for_each = {
    for binding in local.role_bindings : "${binding.environment}-${binding.username}" => binding
    if binding.role == "ml-engineer"
  }
  
  metadata {
    name      = "ml-engineer-${each.value.username}"
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
  }

  subject {
    kind      = "User"
    name      = each.value.username
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    kind      = "Role"
    name      = kubernetes_role.ml_engineer[each.value.environment].metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }
}

# RoleBindings for admins
resource "kubernetes_role_binding" "admin_binding" {
  for_each = {
    for binding in local.role_bindings : "${binding.environment}-${binding.username}" => binding
    if binding.role == "admin"
  }
  
  metadata {
    name      = "admin-${each.value.username}"
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
  }

  subject {
    kind      = "User"
    name      = each.value.username
    api_group = "rbac.authorization.k8s.io"
  }

  role_ref {
    kind      = "Role"
    name      = kubernetes_role.admin[each.value.environment].metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }
}

# Service account roles for application components
resource "kubernetes_role" "app_components" {
  for_each = {
    for component in local.app_components : "${component.environment}-${component.name}" => component
  }
  
  metadata {
    name      = "${each.value.name}-role"
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
  }

  dynamic "rule" {
    for_each = each.value.rules
    
    content {
      api_groups = rule.value.api_groups
      resources  = rule.value.resources
      verbs      = rule.value.verbs
    }
  }
}

# Service account role bindings for application components
resource "kubernetes_role_binding" "app_components" {
  for_each = {
    for component in local.app_components : "${component.environment}-${component.name}" => component
  }
  
  metadata {
    name      = "${each.value.name}-rolebinding"
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = each.value.service_account_name
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
  }

  role_ref {
    kind      = "Role"
    name      = kubernetes_role.app_components[each.key].metadata[0].name
    api_group = "rbac.authorization.k8s.io"
  }
}

# Service accounts for application components
resource "kubernetes_service_account" "app_components" {
  for_each = {
    for component in local.app_components : "${component.environment}-${component.name}" => component
  }
  
  metadata {
    name      = each.value.service_account_name
    namespace = kubernetes_namespace.quantumvestai[each.value.environment].metadata[0].name
    
    annotations = {
      "eks.amazonaws.com/role-arn" = each.value.iam_role_arn
    }
    
    labels = {
      app         = "quantumvestai"
      component   = each.value.name
      environment = each.value.environment
    }
  }
}

# Local variables to define role bindings and application components
locals {
  # Role bindings for different user roles
  role_bindings = flatten([
    for env in var.environments : [
      for binding in var.user_role_bindings : {
        environment = env
        username    = binding.username
        role        = binding.role
      }
    ]
  ])
  
  # Application components with their required permissions
  app_components = flatten([
    for env in var.environments : [
      # API component
      {
        environment         = env
        name                = "api"
        service_account_name = "api-sa"
        iam_role_arn        = var.component_iam_roles["api"]
        rules = [
          {
            api_groups = [""]
            resources  = ["configmaps", "secrets"]
            verbs      = ["get", "list", "watch"]
          },
          {
            api_groups = [""]
            resources  = ["pods"]
            verbs      = ["get", "list"]
          }
        ]
      },
      # Model training component
      {
        environment         = env
        name                = "model-training"
        service_account_name = "model-training-sa"
        iam_role_arn        = var.component_iam_roles["model-training"]
        rules = [
          {
            api_groups = [""]
            resources  = ["configmaps", "secrets", "persistentvolumeclaims"]
            verbs      = ["get", "list", "watch", "create", "update", "patch"]
          },
          {
            api_groups = ["batch"]
            resources  = ["jobs"]
            verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
          }
        ]
      },
      # Scheduler component
      {
        environment         = env
        name                = "scheduler"
        service_account_name = "scheduler-sa"
        iam_role_arn        = var.component_iam_roles["scheduler"]
        rules = [
          {
            api_groups = ["batch"]
            resources  = ["cronjobs", "jobs"]
            verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
          },
          {
            api_groups = [""]
            resources  = ["configmaps", "secrets"]
            verbs      = ["get", "list", "watch"]
          }
        ]
      }
    ]
  ])
}
