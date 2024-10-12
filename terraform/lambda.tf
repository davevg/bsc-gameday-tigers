module "lambda_function_gameday" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = var.project
  description   = "${var.project} accept kafka records"
  handler       = "lambda_function.lambda_handler"
  publish       = true
  runtime       = "python3.12"
  timeout       = 30
  attach_policy_statements = true

  # Policy to allow Lambda to interact with the S3 bucket
  policy_statements = [
    {
      effect = "Allow",
      actions = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ]
      resources = [
        "${aws_s3_bucket.gameday_s3_bucket.arn}",           # The bucket itself
        "${aws_s3_bucket.gameday_s3_bucket.arn}/*"          # Objects within the bucket
      ]
    }
  ]
  create_package = true

  source_path = [
    {
      path             = "${path.module}/lambda"
      pip_requirements = false
    }
  ]

  attach_policies = true
  policies        = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]

  cloudwatch_logs_retention_in_days = 3


}
