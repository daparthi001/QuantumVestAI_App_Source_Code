# EKS Cluster and Node Groups Configuration
# Created: 2025-05-13 20:54:00
# Author: daparthi001

# KMS Key for EKS encryption
resource "aws_kms_key" "eks_key" {
  description             = "KMS key for EKS cluster encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  tags = {
    Name = "${var.project}-${var.environment}-eks-key"
  }
}

resource "aws_kms_alias" "eks_key_alias" {
  name          = "alias/${var.project}-${var.environment}-eks"
  target_key_id = aws_kms_key.eks_key.key_id
}

# IAM Role for EKS Cluster
resource "aws_iam_role" "eks_cluster" {
  name = "${var.cluster_name}-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.cluster_name}-cluster-role"
  }
}

# Attach AmazonEKSClusterPolicy to the cluster role
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
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

  tags = {
    Name = "${var.cluster_name}-cluster-sg"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "eks" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids = module.vpc.private_subnets
    
    security_group_ids = [
      aws_security_group.eks_cluster.id
    ]
    
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  # Enable EKS logging
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  # Encryption configuration
  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_key.arn
    }
    resources = ["secrets"]
  }

  # Ensure IAM Role permissions are created before and deleted after EKS Cluster handling
  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = {
    Name = var.cluster_name
  }
}

# EKS Node Group IAM Role
resource "aws_iam_role" "eks_node" {
  name = "${var.cluster_name}-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.cluster_name}-node-role"
  }
}

# Attach policies to node role
resource "aws_iam_role_policy_attachment" "eks_worker_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.eks_node.name
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.eks_node.name
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.eks_node.name
}

# Standard Node Group
# Standard Node Group with improved configuration
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

  # Use a launch template instead of direct configuration
  launch_template {
    id      = aws_launch_template.standard_nodes.id
    version = aws_launch_template.standard_nodes.latest_version
  }

  # Remove these as they'll be defined in the launch template
  # instance_types = [var.node_instance_type]
  # disk_size      = var.node_disk_size

  labels = {
    "role"        = "standard"
    "environment" = var.environment
  }

  # Add taints if needed
  # taint {
  #   key    = "dedicated"
  #   value  = "standard"
  #   effect = "NO_SCHEDULE"
  # }

  # Enhanced update config to minimize disruptions
  update_config {
    max_unavailable_percentage = 25
  }

  tags = {
    "k8s.io/cluster-autoscaler/enabled" = "true"
    "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
  }

  # Add lifecycle policy to create new nodes before destroying old ones
  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_readonly
  ]
}

# Launch template for standard nodes with enhanced configuration
resource "aws_launch_template" "standard_nodes" {
  name = "${var.cluster_name}-standard-nodes-template"
  
  block_device_mappings {
    device_name = "/dev/xvda"
    
    ebs {
      volume_size           = var.node_disk_size
      volume_type           = "gp3"
      delete_on_termination = true
      encrypted             = true
      # Optional: specify KMS key for encryption
      # kms_key_id            = aws_kms_key.eks_key.arn
    }
  }

  # Enable detailed monitoring
  monitoring {
    enabled = true
  }
  
  # Enable IMDS v2 but make it accessible
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "optional"  # Consider changing to "required" for production
    http_put_response_hop_limit = 2
  }

  # User data script to help with troubleshooting and disk management
  user_data = base64encode(<<-EOT
    #!/bin/bash
    
    # Log startup information
    echo "Node bootstrap starting at $(date)" > /var/log/eks-bootstrap.log
    
    # Add hostname and instance ID to the prompt to help with debugging
    INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
    echo "export PS1='[\u@\h ($INSTANCE_ID) \W]\\$ '" >> /etc/bashrc
    
    # Set up automatic Docker cleanup
    cat > /etc/cron.d/docker-cleanup << EOF
    0 */4 * * * root docker system prune -af --volumes >> /var/log/docker-cleanup.log 2>&1
    EOF
    chmod 644 /etc/cron.d/docker-cleanup
    
    # Set up disk space monitoring and cleanup
    cat > /usr/local/bin/cleanup-disk.sh << 'EOF'
    #!/bin/bash
    LOG="/var/log/disk-cleanup.log"
    echo "=== Running disk cleanup at $(date) ===" >> $LOG
    
    # Check disk usage
    DISK_USAGE=$(df -h / | grep -v Filesystem | awk '{print $5}' | sed 's/%//')
    echo "Current disk usage: $DISK_USAGE%" >> $LOG
    
    if [ $DISK_USAGE -gt 80 ]; then
      echo "Disk usage is high, running cleanup" >> $LOG
      
      # Clean Docker resources
      echo "Cleaning Docker resources" >> $LOG
      docker system prune -af --volumes >> $LOG 2>&1
      
      # Clean log files
      echo "Cleaning log files" >> $LOG
      find /var/log -type f -name "*.log" -size +100M -exec truncate -s 100M {} \; >> $LOG 2>&1
      
      # Clean journald
      echo "Cleaning journald" >> $LOG
      journalctl --vacuum-time=1d >> $LOG 2>&1
      
      # Check disk usage after cleanup
      DISK_USAGE_AFTER=$(df -h / | grep -v Filesystem | awk '{print $5}' | sed 's/%//')
      echo "Disk usage after cleanup: $DISK_USAGE_AFTER%" >> $LOG
    fi
    EOF
    
    chmod +x /usr/local/bin/cleanup-disk.sh
    
    cat > /etc/cron.d/disk-cleanup << EOF
    */30 * * * * root /usr/local/bin/cleanup-disk.sh
    EOF
    chmod 644 /etc/cron.d/disk-cleanup
    
    # Create a diagnostic script
    cat > /usr/local/bin/eks-diagnostics.sh << 'EOF'
    #!/bin/bash
    LOG="/var/log/eks-diagnostics.log"
    echo "=== Running diagnostics at $(date) ===" >> $LOG
    
    # Check system resources
    echo "Memory usage:" >> $LOG
    free -h >> $LOG
    
    echo "Disk usage:" >> $LOG
    df -h >> $LOG
    
    echo "Top processes:" >> $LOG
    ps aux --sort=-%mem | head -10 >> $LOG
    
    # Check network connectivity
    echo "Network connectivity:" >> $LOG
    ping -c 3 8.8.8.8 >> $LOG 2>&1
    
    # Check DNS resolution
    echo "DNS resolution:" >> $LOG
    nslookup kubernetes.default.svc.cluster.local >> $LOG 2>&1
    
    # Check kubelet status
    echo "Kubelet status:" >> $LOG
    systemctl status kubelet >> $LOG 2>&1
    
    # Check kubelet logs
    echo "Recent kubelet logs:" >> $LOG
    journalctl -u kubelet --since "5 minutes ago" | tail -50 >> $LOG
    EOF
    
    chmod +x /usr/local/bin/eks-diagnostics.sh
    
    # Run diagnostics on startup and every 5 minutes
    /usr/local/bin/eks-diagnostics.sh
    
    cat > /etc/cron.d/eks-diagnostics << EOF
    */5 * * * * root /usr/local/bin/eks-diagnostics.sh
    EOF
    chmod 644 /etc/cron.d/eks-diagnostics
    
    # Ensure kubelet is started and enabled
    systemctl enable kubelet
    systemctl start kubelet
    
    echo "Node bootstrap completed at $(date)" >> /var/log/eks-bootstrap.log
  EOT
  )
  
  # Instance tags
  tag_specifications {
    resource_type = "instance"
    
    tags = {
      Name = "${var.cluster_name}-standard-node"
      "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    }
  }
  
  # Volume tags
  tag_specifications {
    resource_type = "volume"
    
    tags = {
      Name = "${var.cluster_name}-standard-node-volume"
      "kubernetes.io/cluster/${var.cluster_name}" = "owned"
    }
  }
}

# ML Node Group (Optional)
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
  disk_size      = var.ml_node_disk_size

  labels = {
    "role"         = "ml-worker"
    "workload-type" = "ml"
    "environment"   = var.environment
  }

  taint {
    key    = "workload-type"
    value  = "ml"
    effect = "NO_SCHEDULE"
  }

  # Fixed the tags syntax - removed the extra braces
  tags = {
    "k8s.io/cluster-autoscaler/enabled" = "true"
    "k8s.io/cluster-autoscaler/${var.cluster_name}" = "owned"
    "k8s.io/cluster-autoscaler/node-template/label/workload-type" = "ml"
  }
  
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_readonly
  ]
}

# OIDC Provider for IAM Roles for Service Accounts (IRSA)
data "tls_certificate" "eks" {
  url = aws_eks_cluster.eks.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.eks.identity[0].oidc[0].issuer
  
  tags = {
    Name = "${var.cluster_name}-oidc-provider"
  }
}

# Optional: Kubeconfig update script
resource "local_file" "kubeconfig_update_script" {
  count    = var.output_kubeconfig_update_script ? 1 : 0
  content  = <<-EOT
    #!/bin/bash
    aws eks update-kubeconfig --region ${var.region} --name ${aws_eks_cluster.eks.name}
    echo "Kubeconfig updated for cluster ${aws_eks_cluster.eks.name}"
  EOT
  filename = "${path.module}/update-kubeconfig.sh"

  # Make script executable
  provisioner "local-exec" {
    command = "chmod +x ${path.module}/update-kubeconfig.sh"
  }
}