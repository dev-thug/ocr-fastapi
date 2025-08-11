resource "aws_ecs_cluster" "this" {
  name = "${var.project_name}-cluster"
}

# Capacity Provider will be linked to ASG (created in asg-gpu.tf)
