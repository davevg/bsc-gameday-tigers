resource "aws_sns_topic" "gameday_notifications" {
  name = "${var.project}-gameday-notifications"
}

resource "aws_sns_topic_subscription" "gameday_email_subscription" {
  count      = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.gameday_notifications.arn
  protocol  = "email"
  endpoint  = var.alert_email
}