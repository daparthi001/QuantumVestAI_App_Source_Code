# RDS Configuration

# Keep all the main RDS resources

# Remove the duplicate kubernetes_secret
# resource "kubernetes_secret" "rds_credentials" { ... }

# Remove all duplicate output blocks:
# - output "rds_endpoint" 
# - output "rds_port"
# - output "rds_database_name"
# - output "rds_secret_name"

# Keep the rest of the RDS resources and configuration