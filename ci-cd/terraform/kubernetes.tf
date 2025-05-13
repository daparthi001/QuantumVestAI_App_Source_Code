# Kubernetes namespace for application deployment
resource "kubernetes_namespace" "quantumvestai" {
  metadata {
    name = "quantumvestai-${var.environment}"
    
    labels = {
      app = "quantumvestai"
      environment = var.environment
      managed-by = "terraform"
    }
  }
}

# Create Kubernetes secret for RDS access
resource "kubernetes_secret" "rds_credentials" {
  metadata {
    name      = "quantumvestai-rds-credentials"
    namespace = kubernetes_namespace.quantumvestai.metadata[0].name
  }

  data = {
    username = var.rds_username
    password = random_password.rds_password.result
    host     = aws_db_instance.quantumvestai.address
    port     = "5432"
    dbname   = var.rds_database_name
    url      = "postgresql://${var.rds_username}:${random_password.rds_password.result}@${aws_db_instance.quantumvestai.address}:5432/${var.rds_database_name}"
  }

  depends_on = [
    kubernetes_namespace.quantumvestai
  ]
}