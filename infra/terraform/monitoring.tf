resource "aws_cloudwatch_log_metric_filter" "app_error" {
  name           = "${var.project_name}-app-error"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "ERROR"
  metric_transformation {
    name      = "${var.project_name}-app-error"
    namespace = var.project_name
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "p95_latency" {
  alarm_name          = "${var.project_name}-p95>5s"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  threshold           = 5
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  extended_statistic  = "p95"
  dimensions = {
    TargetGroup  = aws_lb_target_group.app.arn_suffix
    LoadBalancer = aws_lb.this.arn_suffix
  }
}

resource "aws_cloudwatch_metric_alarm" "gpu_utilization_high" {
  alarm_name          = "${var.project_name}-gpu>80"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  threshold           = 80
  metric_name         = "nvidia_gpu_utilization"
  namespace           = "CWAgent"
  period              = 60
  statistic           = "Average"
}

resource "aws_cloudwatch_metric_alarm" "target_5xx" {
  alarm_name          = "${var.project_name}-tg-5xx>=1"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  threshold           = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  dimensions = {
    TargetGroup  = aws_lb_target_group.app.arn_suffix
    LoadBalancer = aws_lb.this.arn_suffix
  }
}

# Optional: minimal CW dashboard for quick view
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.this.arn_suffix, "TargetGroup", aws_lb_target_group.app.arn_suffix]]
          period  = 60
          stat    = "p95"
          region  = var.aws_region
          title   = "ALB TargetResponseTime p95"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", aws_lb.this.arn_suffix, "TargetGroup", aws_lb_target_group.app.arn_suffix]]
          period  = 60
          stat    = "Sum"
          region  = var.aws_region
          title   = "Target 5xx"
        }
      }
    ]
  })
}

