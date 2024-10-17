resource "aws_sqs_queue" "log_queue" {
  name = var.project
  visibility_timeout_seconds = 300
  message_retention_seconds  = 86400
}