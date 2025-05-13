# Additional EKS variables

variable "model_storage_bucket" {
  description = "S3 bucket name for storing ML models"
  type        = string
  default     = "quantumvestai-models"
}

# Variable for EKS addon versions
variable "eks_addon_versions" {
  description = "Versions for EKS addons"
  type        = map(string)
  default     = {
    vpc_cni              = "v1.12.6-eksbuild.2"
    kube_proxy           = "v1.26.6-eksbuild.1"
    coredns              = "v1.9.3-eksbuild.5"
    aws_ebs_csi_driver   = "v1.19.0-eksbuild.2"
  }
}

# Variable for Kubernetes addons
variable "k8s_addons" {
  description = "Whether to install Kubernetes addons"
  type        = map(bool)
  default     = {
    metrics_server       = true
    cluster_autoscaler   = true
    prometheus           = true
    aws_load_balancer    = true
  }
}