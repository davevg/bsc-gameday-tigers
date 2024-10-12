# Policies needed to allow EKS to invoke Lambda
resource "aws_iam_policy" "invoke_lambda_policy" {
  name        = "InvokeLambdaPolicy"
  description = "Policy to allow invoking AWS Lambda from EKS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "lambda:InvokeFunction",
        Resource = "arn:aws:lambda:${var.region}:${var.account_id}:function:${var.project}"
      }
    ]
  })
}


resource "aws_iam_role" "eks_pod_role" {
  name = "${var.project}-lambda-invoke-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = "arn:aws:iam::${var.account_id}:oidc-provider/${var.eks_oidc_provider}"
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          "StringEquals" = {
            "${var.eks_oidc_provider}:sub" = "system:serviceaccount:${var.namespace}:${var.service_account_name}"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_invoke_lambda_policy" {
  role       = aws_iam_role.eks_pod_role.name
  policy_arn = aws_iam_policy.invoke_lambda_policy.arn
}