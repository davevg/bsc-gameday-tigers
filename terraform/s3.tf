resource "aws_s3_bucket" "gameday_s3_bucket" {
  bucket = "bsc-2024-gameday-tigers"
}

data "aws_iam_policy_document" "s3_bucket_policy" {
  statement {
    effect = "Allow"
    actions = [
        "s3:PutObject",
        "s3:GetObjectVersion",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:DeleteObjectVersion"
    ]
    resources = [
      aws_s3_bucket.gameday_s3_bucket.arn,
      "${aws_s3_bucket.gameday_s3_bucket.arn}/*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
        "s3:ListBucket",
        "s3:GetBucketLocation"
    ]
    resources = [
      aws_s3_bucket.gameday_s3_bucket.arn
    ]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values = ["*"]
    } 
  }
} 

resource "aws_iam_policy" "policy" {
  name        =  "${var.project}_policy"
  description = "Policy to allow access to project bucket"
  policy = data.aws_iam_policy_document.s3_bucket_policy.json
}