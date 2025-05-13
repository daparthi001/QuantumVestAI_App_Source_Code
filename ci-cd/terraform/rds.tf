# Amazon RDS for model training data and prediction results

# Security group for RDS
resource "aws_security_group" "rds_sg" {
  name        = "quantumvestai-rds-sg-${var.environment}"
  description = "Security group for QuantumVestAI RDS instance"
  vpc_id      = module.vpc.vpc_id

  # Allow incoming traffic from EKS nodes
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
    description     = "Allow PostgreSQL traffic from EKS nodes"
  }

  # Allow outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    local.tags,
    {
      Name = "quantumvestai-rds-sg-${var.environment}"
    }
  )
}

# RDS Subnet Group
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "quantumvestai-rds-subnet-group-${var.environment}"
  subnet_ids = module.vpc.private_subnets
  
  tags = merge(
    local.tags,
    {
      Name = "quantumvestai-rds-subnet-group-${var.environment}"
    }
  )
}

# Random password generator for RDS
resource "random_password" "rds_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store RDS credentials in AWS Secrets Manager
resource "aws_secretsmanager_secret" "rds_credentials" {
  name        = "quantumvestai-rds-credentials-${var.environment}"
  description = "RDS credentials for QuantumVestAI ${var.environment} environment"
  
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "rds_credentials" {
  secret_id = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode({
    username = var.rds_username
    password = random_password.rds_password.result
    host     = aws_db_instance.quantumvestai.address
    port     = aws_db_instance.quantumvestai.port
    dbname   = var.rds_database_name
    engine   = "postgres"
  })
}

# RDS Parameter Group
resource "aws_db_parameter_group" "postgres" {
  name   = "quantumvestai-postgres-params-${var.environment}"
  family = "postgres14"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory/4096}"
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "work_mem"
    value = "16384"
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "1048576"
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory/2048}"
    apply_method = "pending-reboot"
  }

  parameter {
    name  = "autovacuum"
    value = "1"
  }

  tags = local.tags
}

# RDS Instance
resource "aws_db_instance" "quantumvestai" {
  identifier           = "quantumvestai-${var.environment}"
  engine               = "postgres"
  engine_version       = "14.6"
  instance_class       = var.rds_instance_class
  allocated_storage    = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage
  storage_type         = "gp3"
  storage_encrypted    = true

  db_name              = var.rds_database_name
  username             = var.rds_username
  password             = random_password.rds_password.result
  port                 = 5432

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  parameter_group_name   = aws_db_parameter_group.postgres.name

  # Backup settings
  backup_retention_period = var.environment == "prod" ? 30 : 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"
  
  # Enable deletion protection in production
  deletion_protection     = var.environment == "prod" ? true : false
  
  # Enable Multi-AZ for production
  multi_az                = var.environment == "prod" ? true : false
  
  # Enable enhanced monitoring
  monitoring_interval     = 60
  monitoring_role_arn     = aws_iam_role.rds_monitoring_role.arn
  
  # Enable performance insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  # Disable public access
  publicly_accessible     = false
  
  # Enable auto minor version upgrade
  auto_minor_version_upgrade = true
  
  # Apply changes immediately (use carefully in production)
  apply_immediately       = var.environment != "prod"

  # Snapshot settings
  skip_final_snapshot     = var.environment != "prod"
  final_snapshot_identifier = var.environment != "prod" ? null : "quantumvestai-${var.environment}-final-${formatdate("YYYYMMDDhhmmss", timestamp())}"
  
  tags = merge(
    local.tags,
    {
      Name = "quantumvestai-${var.environment}"
    }
  )

  lifecycle {
    prevent_destroy = var.environment == "prod"
  }
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_monitoring_role" {
  name = "quantumvestai-rds-monitoring-role-${var.environment}"
  
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
  
  tags = local.tags
}

# Attach the AWS managed policy for RDS Enhanced Monitoring
resource "aws_iam_role_policy_attachment" "rds_monitoring_attachment" {
  role       = aws_iam_role.rds_monitoring_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Create Kubernetes secret for RDS access
resource "kubernetes_secret" "rds_credentials" {
  metadata {
    name      = "quantumvestai-rds-credentials"
    namespace = "quantumvestai-${var.environment}"
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

# Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.quantumvestai.endpoint
  sensitive   = false
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.quantumvestai.db_name
  sensitive   = false
}

output "rds_username" {
  description = "RDS master username"
  value       = aws_db_instance.quantumvestai.username
  sensitive   = false
}

output "rds_secret_name" {
  description = "Name of the AWS Secrets Manager secret containing RDS credentials"
  value       = aws_secretsmanager_secret.rds_credentials.name
  sensitive   = false
}