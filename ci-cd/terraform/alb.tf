resource "aws_lb" "app" {
  name               = "dummy-alb-quantumvestai"
  internal           = false
  load_balancer_type = "application"
  security_groups    = []
  subnets            = ["subnet-abc123"]  # Replace with real subnet IDs

  enable_deletion_protection = false
}