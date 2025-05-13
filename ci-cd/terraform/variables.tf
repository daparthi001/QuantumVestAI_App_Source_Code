variable "region" {
  default     = "us-east-1"
  description = "AWS region"
}

variable "cluster_name" {
  default     = "quantumai"
  description = "EKS cluster name"
}

variable "env" {
  default     = "dev"
}

variable "node_instance_type" {
  default     = "t3.medium"
  description = "Instance type for worker nodes"
}

variable "desired_nodes" {
  default     = 1
  description = "Desired number of worker nodes"
}

variable "iam_user_arn" {
  default     = "arn:aws:iam::921930869047:user/admin-user" # Replace with actual IAM user ARN
  description = "IAM user ARN for Kubernetes access"
}