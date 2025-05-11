resource "aws_ecr_repository" "quantumvestai" {
  name = "quantumvestai"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Name        = "quantumvestai"
    Environment = "production"
  }
}