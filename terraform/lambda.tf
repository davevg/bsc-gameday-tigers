module "lambda_function_gameday" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = var.project
  description   = "${var.project} accept kafka records"
  handler       = "lambda_function.lambda_handler"
  publish       = true
  runtime       = "python3.12"
  timeout       = 30
  attach_policy_statements = true
  memory_size   = 256
  environment_variables = {
    SAGEMAKER_ENDPOINT = var.sagemaker_endpoint_name
    S3_BUCKET_NAME     = aws_s3_bucket.gameday_s3_bucket.bucket
    SQS_QUEUE_URL      = aws_sqs_queue.log_queue.url
    MODEL_METADATA_FILE = var.model_metadata_file
  }
  layers                 = [    
    aws_lambda_layer_version.sklearn-layer.arn
  ]
  # Policy to allow Lambda to interact with the S3 bucket
  policy_statements = [
    {
      effect = "Allow",
      actions = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      resources = [
        "${aws_s3_bucket.gameday_s3_bucket.arn}",           # The bucket itself
        "${aws_s3_bucket.gameday_s3_bucket.arn}/*"          # Objects within the bucket
      ]
    },
    {
      effect = "Allow",
      actions = [
        "sagemaker:InvokeEndpoint"
      ],
      resources = ["*"]
    },
   {
    effect = "Allow",
    actions = [
      "sqs:SendMessage"                                   # Allow publishing to SQS
    ],
    resources = [
      "${aws_sqs_queue.log_queue.arn}"                    # ARN of the SQS queue
    ]
    }   
  ]
  create_package = true

  source_path = [
    {
      path             = "${path.module}/lambda/consumer"
      pip_requirements = false
    }
  ]

  attach_policies = true
  policies        = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  cloudwatch_logs_retention_in_days = 7
}

resource "aws_lambda_layer_version" "sklearn-layer" {
    layer_name          = "sklearn"
    s3_bucket = aws_s3_bucket.gameday_s3_bucket.bucket
    s3_key = "lambda/layers/sklearn_3_12_x86_64.zip"
    compatible_runtimes = ["python3.12"]
    depends_on = [ aws_s3_object.sklearn-layer ]
}


resource "aws_s3_object" "sklearn-layer" {
  bucket       = aws_s3_bucket.gameday_s3_bucket.bucket
  key          = "lambda/layers/sklearn_3_12_x86_64.zip"
  source       = "./lambda/lambda_layers/sklearn_3_12_x86_64.zip"
  source_hash  = filemd5("./lambda/lambda_layers/sklearn_3_12_x86_64.zip")
}

module "lambda_function_gameday_sqs" {
  source = "terraform-aws-modules/lambda/aws"
  function_name = "${var.project}-sqs"
  handler       = "lambda_function.lambda_handler"
  publish       = true
  runtime       = "python3.12"
  timeout       = 900
  memory_size   = 256
  attach_policy_statements = true

  environment_variables = {
    QUEUE_URL      = aws_sqs_queue.log_queue.id
    S3_BUCKET_NAME = aws_s3_bucket.gameday_s3_bucket.bucket
  }
  policy_statements = [
    {
      effect = "Allow",
      actions = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      resources = [
        "${aws_s3_bucket.gameday_s3_bucket.arn}",           # The bucket itself
        "${aws_s3_bucket.gameday_s3_bucket.arn}/*"          # Objects within the bucket
      ]
    },
   {
    effect = "Allow",
    actions = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
    ],
    resources = [
      "${aws_sqs_queue.log_queue.arn}"                    # ARN of the SQS queue
    ]
    }   
  ]  
  create_package = true

  source_path = [
    {
      path             = "${path.module}/lambda/lambda_sqs"
      pip_requirements = false
    }
  ]

  attach_policies = true
  policies        = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  cloudwatch_logs_retention_in_days = 7  
}

