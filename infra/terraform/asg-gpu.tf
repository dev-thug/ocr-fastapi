data "aws_ami" "ecs_gpu" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-gpu-hvm-*-x86_64-ebs"]
  }
}

resource "aws_launch_template" "gpu" {
  name_prefix   = "${var.project_name}-gpu-"
  image_id      = data.aws_ami.ecs_gpu.id
  instance_type = var.instance_type

  metadata_options {
    http_tokens = "required"
  }

  tag_specifications {
    resource_type = "instance"
    tags          = { Name = "${var.project_name}-gpu" }
  }
}

resource "aws_autoscaling_group" "gpu" {
  name                = "${var.project_name}-gpu-asg"
  desired_capacity    = var.asg_min_size
  min_size            = var.asg_min_size
  max_size            = var.asg_max_size
  vpc_zone_identifier = [aws_subnet.private[0].id, aws_subnet.private[1].id]
  health_check_type   = "EC2"

  mixed_instances_policy {
    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.gpu.id
        version            = "$Latest"
      }
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_ecs_capacity_provider" "gpu" {
  name = "${var.project_name}-gpu-cp"
  auto_scaling_group_provider {
    auto_scaling_group_arn = aws_autoscaling_group.gpu.arn
    managed_scaling { status = "ENABLED" }
    managed_termination_protection = "ENABLED"
  }
}

resource "aws_ecs_cluster_capacity_providers" "attach" {
  cluster_name       = aws_ecs_cluster.this.name
  capacity_providers = [aws_ecs_capacity_provider.gpu.name]
  default_capacity_provider_strategy { capacity_provider = aws_ecs_capacity_provider.gpu.name }
}
