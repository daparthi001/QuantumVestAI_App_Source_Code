# Amazon RDS Configuration for QuantumVestAI (Continued)

# Complete the IAM Role for RDS Monitoring
resource "aws_iam_role" "rds_monitoring_role" {
  name = "${var.project_name}-rds-monitoring-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    local.common_tags,
    {
      Name = "${var.project_name}-rds-monitoring-role-${var.environment}"
    }
  )
}

# Attach the AWS managed policy for RDS Enhanced Monitoring
resource "aws_iam_role_policy_attachment" "rds_monitoring_attachment" {
  role       = aws_iam_role.rds_monitoring_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Secrets Manager Secret for RDS Credentials
resource "aws_secretsmanager_secret" "rds_credentials" {
  count = var.rds_enabled ? 1 : 0
  
  name        = "${var.project_name}-rds-credentials-${var.environment}"
  description = "RDS credentials for ${var.project_name} ${var.environment} environment"
  
  tags = local.common_tags
}

# Secrets Manager Secret Version
resource "aws_secretsmanager_secret_version" "rds_credentials" {
  count = var.rds_enabled ? 1 : 0
  
  secret_id = aws_secretsmanager_secret.rds_credentials[0].id
  secret_string = jsonencode({
    username = var.rds_username
    password = random_password.rds_password.result
    host     = aws_db_instance.quantumvestai[0].endpoint
    port     = aws_db_instance.quantumvestai[0].port
    dbname   = aws_db_instance.quantumvestai[0].db_name
    engine   = "postgres"
    jdbc_url = "jdbc:postgresql://${aws_db_instance.quantumvestai[0].endpoint}/${aws_db_instance.quantumvestai[0].db_name}"
  })
}

# Kubernetes Secret for RDS Credentials (Optional)
resource "kubernetes_secret" "rds_credentials" {
  count = var.rds_enabled ? 1 : 0
  
  metadata {
    name      = "${var.project_name}-rds-credentials"
    namespace = "default"  # Consider using a more specific namespace
  }
  
  type = "Opaque"
  
  data = {
    USERNAME = base64encode(var.rds_username)
    PASSWORD = base64encode(random_password.rds_password.result)
    HOST     = base64encode(aws_db_instance.quantumvestai[0].endpoint)
    PORT     = base64encode(tostring(aws_db_instance.quantumvestai[0].port))
    DATABASE = base64encode(aws_db_instance.quantumvestai[0].db_name)
    JDBC_URL = base64encode("jdbc:postgresql://${aws_db_instance.quantumvestai[0].endpoint}/${aws_db_instance.quantumvestai[0].db_name}")
  }
}

# CloudWatch Alarm for RDS High CPU Utilization
resource "aws_cloudwatch_metric_alarm" "rds_high_cpu" {
  count = var.rds_enabled ? 1 : 0
  
  alarm_name          = "${var.project_name}-rds-high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Average database CPU utilization is too high."
  alarm_actions       = [aws_sns_topic.rds_alerts[0].arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.quantumvestai[0].identifier
  }

  tags = local.common_tags
}

# CloudWatch Alarm for RDS Free Storage Space
resource "aws_cloudwatch_metric_alarm" "rds_low_storage" {
  count = var.rds_enabled ? 1 : 0
  
  alarm_name          = "${var.project_name}-rds-low-storage-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "5368709120"  # 5 GB in bytes
  alarm_description   = "Database is running low on storage space."
  alarm_actions       = [aws_sns_topic.rds_alerts[0].arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.quantumvestai[0].identifier
  }

  tags = local.common_tags
}

# SNS Topic for RDS Alerts
resource "aws_sns_topic" "rds_alerts" {
  count = var.rds_enabled ? 1 : 0
  
  name = "${var.project_name}-rds-alerts-${var.environment}"
  
  tags = local.common_tags
}

# Optional SNS Topic Subscription
resource "aws_sns_topic_subscription" "rds_alerts_email" {
  count = var.rds_enabled && var.alarm_email != "" ? 1 : 0
  
  topic_arn = aws_sns_topic.rds_alerts[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# Outputs
output "rds_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = var.rds_enabled ? aws_db_instance.quantumvestai[0].endpoint : null
  sensitive   = true
}

output "rds_port" {
  description = "Port of the RDS instance"
  value       = var.rds_enabled ? aws_db_instance.quantumvestai[0].port : null
}

output "rds_database_name" {
  description = "Name of the RDS database"
  value       = var.rds_enabled ? aws_db_instance.quantumvestai[0].db_name : null
}

output "rds_username" {
  description = "Username for the RDS instance"
  value       = var.rds_enabled ? aws_db_instance.quantumvestai[0].username : null
  sensitive   = true
}

output "rds_secret_name" {
  description = "Name of the Secrets Manager secret containing RDS credentials"
  value       = var.rds_enabled ? aws_secretsmanager_secret.rds_credentials[0].name : null
  sensitive   = true
}