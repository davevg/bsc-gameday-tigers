locals {
    log_group_name = "/aws/lambda/${var.project}"
    encoded_log_group_name = replace(local.log_group_name, "/", "%252F")
}

# Metric filter for "Result: Normal"
resource "aws_cloudwatch_log_metric_filter" "normal_metric" {
  name = "ResultNormalMetric"
  log_group_name = local.log_group_name

  pattern = "\"Result: Normal\""  # Pattern to match logs containing "Result: Normal"

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

  pattern = "\"Result: High Outlier\""  # Pattern to match logs containing "Result: High Outlier"

  metric_transformation {
    name = "ResultHighOutlierCount"
    namespace = format("/bsc/gameday2024/%s", var.project)
    value = "1"
  }
}

# Metric filter for "Result: Low Outlier"
resource "aws_cloudwatch_log_metric_filter" "low_outlier_metric" {
  name = "ResultLowOutlierMetric"
  log_group_name = local.log_group_name

  pattern = "\"Result: Low Outlier\""  # Pattern to match logs containing "Result: Low Outlier"

  metric_transformation {
    name = "ResultLowOutlierCount"
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
            [ "/bsc/gameday2024/${var.project}", "ResultHighOutlierCount" ],
            [ "/bsc/gameday2024/${var.project}", "ResultLowOutlierCount" ]
          ],
          "view" : "timeSeries",
          "stacked" : false,
          "region" : "${var.region}",
          "stat" : "Sum",
          "period" : 300,
          "title" : "Gameday Metrics: Normal, High Outlier, Low Outlier"
        }
      },
    {
        "type": "log",
        "x": 0,
        "y": 6,
        "width": 24,
        "height": 6,
        "properties": {
            "query": "SOURCE '${local.log_group_name}' | fields @timestamp, @message, @logStream, @log\n| filter @message like 'Result: High Outlier'\n| sort @timestamp desc\n| limit 10000",
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
            "query": "SOURCE '${local.log_group_name}' | fields @timestamp, @message, @logStream, @log\n| filter @message like 'Result: Low Outlier'\n| sort @timestamp desc\n| limit 10000",
            "region": "us-east-1",
            "stacked": false,
            "view": "table"
            "title": "Low Outlier Logs"
        }
    },
    {
        "type": "log",
        "x": 0,
        "y": 18,
        "width": 24,
        "height": 6,
        "properties": {
            "query": "SOURCE '${local.log_group_name}' | fields @timestamp, @message, @logStream, @log\n| filter @message like 'Result: Normal'\n| sort @timestamp desc\n| limit 10000",
            "region": "us-east-1",
            "stacked": false,
            "view": "table"
            "title": "Normal Logs"
        }
    }     
    ]
  })
}