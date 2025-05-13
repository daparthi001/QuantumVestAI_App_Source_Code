resource "aws_lb" "app" {
  name               = "dummy-alb-quantumvestai"
  internal           = false
  load_balancer_type = "application"
  subnets            = module.vpc.public_subnets

  enable_deletion_protection = false
}