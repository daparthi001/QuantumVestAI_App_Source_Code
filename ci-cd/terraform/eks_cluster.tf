# EKS Cluster and Node Groups

resource "aws_eks_cluster" "eks" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.eks_cluster.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  # Enable EKS logging
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  # Ensure IAM Role permissions are created before and deleted after EKS Cluster handling
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = local.tags
}

# Security group for EKS cluster
resource "aws_security_group" "eks_cluster" {
  name        = "${var.cluster_name}-cluster-sg"
  description = "Security group for EKS cluster"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS traffic for Kubernetes API"
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.cluster_name}-cluster-sg"
    }
  )
}

# Security group for EKS nodes
resource "aws_security_group" "eks_nodes" {
  name        = "${var.cluster_name}-node-sg"
  description = "Security group for EKS worker nodes"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  # Allow nodes to communicate with each other
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "-1"
    self        = true
    description = "Allow nodes to communicate with each other"
  }

  # Allow worker nodes to communicate with the cluster API
  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "Allow pods to communicate with the cluster API"
  }

  # Allow cluster control plane to communicate with worker nodes
  ingress {
    from_port       = 1025
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
    description     = "Allow cluster control plane to communicate with worker nodes"
  }

  tags = merge(
    local.tags,
    {
      Name = "${var.cluster_name}-node-sg"
    }
  )
}

# EKS Node Group - Standard
resource "aws_eks_node_group" "standard" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "${var.cluster_name}-standard-nodes"
  node_role_arn   = aws_iam_role.eks_node.arn
  subnet_ids      = module.vpc.private_subnets

  scaling_config {
    desired_size = var.desired_nodes
    max_size     = var.max_nodes
    min_size     = var.min_nodes
  }

  instance_types = [var.node_instance_type]

  # Disk configuration
  disk_size = var.node_disk_size

  # Node labels
  labels = {
    "role" = "standard"
    "environment" = var.environment
  }

  # Enable cluster autoscaler tags
  tags = merge(
    local.tags,
    {
      "k8s.io/cluster-autoscaler/enabled" = "true",
      "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
    }
  )

  # Update configuration
  update_config {
    max_unavailable = 1
  }

  # Ensure IAM Role permissions are created before and deleted after EKS Node Group handling
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_readonly
  ]
}

# EKS Node Group - ML (for AI/ML workloads)
resource "aws_eks_node_group" "ml" {
  count = var.enable_ml_nodes ? 1 : 0

  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "${var.cluster_name}-ml-nodes"
  node_role_arn   = aws_iam_role.eks_node.arn
  subnet_ids      = module.vpc.private_subnets

  scaling_config {
    desired_size = var.ml_desired_nodes
    max_size     = var.ml_max_nodes
    min_size     = var.ml_min_nodes
  }

  instance_types = [var.ml_node_instance_type]

  # Disk configuration
  disk_size = var.ml_node_disk_size

  # Node labels and taints
  labels = {
    "role" = "ml-worker"
    "workload-type" = "ml"
    "environment" = var.environment
  }
  
  taint {
    key    = "workload-type"
    value  = "ml"
    effect = "NO_SCHEDULE"
  }

  # Enable cluster autoscaler tags
  tags = merge(
    local.tags,
    {
      "k8s.io/cluster-autoscaler/enabled" = "true",
      "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned",
      "k8s.io/cluster-autoscaler/node-template/label/workload-type" = "ml"
    }
  )

  # Update configuration
  update_config {
    max_unavailable = 1
  }

  # Ensure IAM Role permissions are created before and deleted after EKS Node Group handling
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_readonly
  ]
}

# EKS OIDC Provider for IAM Roles for Service Accounts (IRSA)
data "tls_certificate" "eks" {
  url = aws_eks_cluster.eks.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.eks.identity[0].oidc[0].issuer
}

# Kubeconfig update script
resource "local_file" "kubeconfig_update_script" {
  count    = var.output_kubeconfig_update_script ? 1 : 0
  content  = <<-EOT
    #!/bin/bash
    aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.eks.name}
    echo "Kubeconfig updated for cluster ${aws_eks_cluster.eks.name}"
  EOT
  filename = "${path.module}/update-kubeconfig.sh"

  # Make script executable
  provisioner "local-exec" {
    command = "chmod +x ${path.module}/update-kubeconfig.sh"
  }
}
