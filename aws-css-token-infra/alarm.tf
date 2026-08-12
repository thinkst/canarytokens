resource "aws_cloudwatch_metric_alarm" "css_function_errors" {
  alarm_name          = var.function_error_alarm_name
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  threshold           = 2

  namespace   = "AWS/CloudFront"
  metric_name = "FunctionExecutionErrors"
  statistic   = "Average"
  period      = 300

  dimensions = {
    FunctionName = var.function_error_alarm_function_name
    Region       = "Global"
  }

  alarm_actions      = var.alarm_actions
  treat_missing_data = "missing"

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [alarm_description]
  }
}

resource "aws_cloudwatch_metric_alarm" "distribution_http_5xx_error_rate" {
  alarm_name          = var.http_5xx_alarm_name
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  threshold           = 0

  namespace   = "AWS/CloudFront"
  metric_name = "5xxErrorRate"
  statistic   = "Average"
  period      = 300

  dimensions = {
    DistributionId = var.distribution_id
  }

  alarm_actions      = var.alarm_actions
  treat_missing_data = "notBreaching"

  lifecycle {
    prevent_destroy = true
  }
}
