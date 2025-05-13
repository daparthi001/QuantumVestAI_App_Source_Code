# Variables for RDS configuration

variable "rds_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  description = "Allocated storage for RDS instance (in GB)"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance (in GB)"
  type        = number
  default     = 100
}

variable "rds_database_name" {
  description = "Name of the database to create"
  type        = string
  default     = "quantumvestai"
}

variable "rds_username" {
  description = "Username for the RDS instance"
  type        = string
  default     = "quantumvestai"
}

variable "rds_backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "rds_storage_encrypted" {
  description = "Specifies whether the DB instance is encrypted"
  type        = bool
  default     = true
}

variable "rds_multi_az" {
  description = "Specifies if the RDS instance is multi-AZ"
  type        = bool
  default     = false
}

variable "rds_publicly_accessible" {
  description = "Specifies if the RDS instance is publicly accessible"
  type        = bool
  default     = false
}

variable "rds_skip_final_snapshot" {
  description = "Determines whether a final DB snapshot is created before the DB instance is deleted"
  type        = bool
  default     = true
}

variable "rds_final_snapshot_identifier" {
  description = "The name of your final DB snapshot when this DB instance is deleted"
  type        = string
  default     = null
}

variable "rds_apply_immediately" {
  description = "Specifies whether any database modifications are applied immediately"
  type        = bool
  default     = false
}

variable "rds_monitoring_interval" {
  description = "The interval, in seconds, between points when Enhanced Monitoring metrics are collected for the DB instance"
  type        = number
  default     = 60
}

variable "rds_performance_insights_enabled" {
  description = "Specifies whether Performance Insights are enabled"
  type        = bool
  default     = true
}

variable "rds_performance_insights_retention_period" {
  description = "The amount of time in days to retain Performance Insights data"
  type        = number
  default     = 7
}

variable "rds_enabled" {
  description = "Whether to create the RDS instance"
  type        = bool
  default     = true
}

variable "db_parameter_group_family" {
  description = "The family of the DB parameter group"
  type        = string
  default     = "postgres14"
}

variable "db_parameter_group_parameters" {
  description = "A list of DB parameter group parameters"
  type        = list(map(string))
  default     = []
}