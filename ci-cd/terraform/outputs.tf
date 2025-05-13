output "eks_cluster_name" {
  value = var.cluster_name
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
