locals {
    log_group_name = "/aws/lambda/${var.project}"
    encoded_log_group_name = replace(local.log_group_name, "/", "%252F")
}

# Metric filter for "Result: Normal"
resource "aws_cloudwatch_log_metric_filter" "normal_metric" {
  name = "ResultNormalMetric"
  log_group_name = local.log_group_name

  pattern = "\"Result: Normal\""

  metric_transformation {
    name = "ResultNormalCount"
    namespace = format("/bsc/gameday2024/%s", var.project)
    value = "1"
  }
}

# Metric filter for "Result: High Outlier"
resource "aws_cloudwatch_log_metric_filter" "high_outlier_metric" {
  name = "ResultHighOutlierMetric"
  log_group_name = local.log_group_name

  pattern = "\"Result: High Outlier\""

  metric_transformation {
    name = "ResultHighOutlierCount"
    namespace = format("/bsc/gameday2024/%s", var.project)
    value = "1"
  }
}

resource "aws_cloudwatch_dashboard" "gameday_dashboard" {
  dashboard_name = "Tigers-GamedayMetricsDashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        "type" : "metric",
        "x" : 0,
        "y" : 0,
        "width" : 24,
        "height" : 6,
        "properties" : {
          "metrics" : [
            [ "/bsc/gameday2024/${var.project}", "ResultNormalCount" ],
            [ "/bsc/gameday2024/${var.project}", "ResultHighOutlierCount" ]
          ],
          "view" : "timeSeries",
          "stacked" : false,
          "region" : "${var.region}",
          "stat" : "Sum",
          "period" : 300,
          "title" : "Gameday Metrics: Normal & Outlier"
        }
      },
    {
        "type": "log",
        "x": 0,
        "y": 6,
        "width": 24,
        "height": 6,
        "properties": {
            "query": "SOURCE '${local.log_group_name}' | fields @timestamp, @message, @logStream\n| filter @message like 'Result: High Outlier'\n| sort @timestamp desc\n| limit 10000",
            "region": "us-east-1",
            "stacked": false,
            "view": "table"
            "title": "High Outlier Logs"
        }
    },
    {
        "type": "log",
        "x": 0,
        "y": 12,
        "width": 24,
        "height": 6,
        "properties": {
            "query": "SOURCE '${local.log_group_name}' | fields @timestamp, @message, @logStream\n| filter @message like 'Result: Normal'\n| sort @timestamp desc\n| limit 10000",
            "region": "us-east-1",
            "stacked": false,
            "view": "table"
            "title": "Normal Logs"
        }
    }     
    ]
  })
}

resource "aws_cloudwatch_event_rule" "hourly_event" {
  name                = "${var.project}-hourly-sqs-consumer"
  schedule_expression = "rate(1 hour)"  # Run every hour
}
resource "aws_cloudwatch_event_target" "event_target" {
  rule      = aws_cloudwatch_event_rule.hourly_event.name
  target_id = "sqs-consumer-lambda"
  arn       = module.lambda_function_gameday_sqs.lambda_function_arn
}
resource "aws_lambda_permission" "allow_eventbridge_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_function_gameday_sqs.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.hourly_event.arn
}



resource "aws_cloudwatch_metric_alarm" "anomaly_alarm" {
  alarm_name          = "${var.project}-GamedayAnomalyAlarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1  # One evaluation period of 15 minutes
  threshold           = 5  # Alarm when more than 5 anomalies detected
  alarm_description   = "Triggers when more than 5 anomalies (high outliers) are detected within 15 minutes"
  actions_enabled     = true
  treat_missing_data   = "notBreaching"
  # Metric query for High Outliers
  metric_query {
      id          = "m1" 
      period      = 0 
      return_data = false 

      metric {
          dimensions  = {} 
          metric_name = "ResultHighOutlierCount" 
          namespace   = "/bsc/gameday2024/${var.project}" 
          period      = 900 
          stat        = "Sum" 
        }
    }
    metric_query {
      expression  = "SUM(METRICS())"
      id          = "e1" 
      label       = "Outliers" 
      period      = 0 
      return_data = true 
    }
  alarm_actions = [ ]

}