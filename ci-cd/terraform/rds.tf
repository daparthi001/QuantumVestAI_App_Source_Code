# RDS Database Configuration
# Created: 2025-05-13 20:52:42
# Author: daparthi001

# KMS Key for RDS encryption
resource "aws_kms_key" "rds_key" {
  description             = "KMS key for RDS database encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  tags = {
    Name = "${var.project}-${var.environment}-rds-key"
  }
}

resource "aws_kms_alias" "rds_key_alias" {
  name          = "alias/${var.project}-${var.environment}-rds"
  target_key_id = aws_kms_key.rds_key.key_id
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "${var.project}-${var.environment}-rds-sg"
  description = "Security group for RDS database"
  vpc_id      = module.vpc.vpc_id

  # Allow only PostgreSQL traffic from the EKS cluster nodes
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "Allow PostgreSQL traffic from EKS cluster"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
}

# Subnet group for RDS
resource "aws_db_subnet_group" "main" {
  name       = "${var.project}-${var.environment}-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.project}-${var.environment}-subnet-group"
  }
}

# Random password generator for RDS
resource "random_password" "rds_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = "${var.project}-${var.environment}-pg"
  family = "postgres14"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  tags = {
    Name = "${var.project}-${var.environment}-pg"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier             = "${var.project}-${var.environment}"
  engine                 = "postgres"
  engine_version         = "14.16"
  instance_class         = var.rds_instance_class
  allocated_storage      = var.rds_allocated_storage
  max_allocated_storage  = var.rds_max_allocated_storage
  storage_type           = "gp3"
  storage_encrypted      = true
  kms_key_id             = aws_kms_key.rds_key.arn
  db_name                = var.rds_database_name
  username               = var.rds_username
  password               = random_password.rds_password.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.main.name
  publicly_accessible    = false
  skip_final_snapshot    = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.project}-${var.environment}-final-snapshot" : null
  backup_retention_period = var.environment == "prod" ? 7 : 1
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:30-sun:05:30"
  auto_minor_version_upgrade = true
  deletion_protection      = var.environment == "prod"
  
  tags = {
    Name = "${var.project}-${var.environment}-rds"
  }
}

# Store RDS credentials in Kubernetes secret
resource "kubernetes_secret" "rds_credentials" {
  metadata {
    name      = "${var.cluster_name}-rds-credentials"
    namespace = "default"
  }

  data = {
    username = aws_db_instance.main.username
    password = random_password.rds_password.result
    endpoint = aws_db_instance.main.endpoint
    port     = tostring(aws_db_instance.main.port)
    database = aws_db_instance.main.db_name
  }

  type = "Opaque"

  depends_on = [aws_db_instance.main, aws_eks_cluster.eks]
}