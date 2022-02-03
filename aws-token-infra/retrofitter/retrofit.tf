provider "aws" {
   region = "us-east-2"
}

data "aws_caller_identity" "current" {}

variable "api_tokens_safety_net_name" {
  default = "APITokensSafetyNet"
}

resource "aws_dynamodb_table" "awsidtoken_table" {
  name           = "awsidtoken_table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "Username"

  attribute {
    name = "Username"
    type = "S"
  }
}

resource "aws_iam_role" "api_tokens_safety_net" {
  name = "SafetyNetRole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "api_tokens_safety_net" {
  filename      = "../lambdas/${var.api_tokens_safety_net_name}/lambda_function_payload.zip"
  function_name = var.api_tokens_safety_net_name
  role          = aws_iam_role.api_tokens_safety_net.arn
  handler       = "lambda_function.lambda_handler"
  source_code_hash = filebase64sha256("../lambdas/${var.api_tokens_safety_net_name}/lambda_function_payload.zip")
  timeout       = 600

  runtime = "python3.9"

  depends_on = [
    aws_iam_role_policy_attachment.api_tokens_safety_net,
    aws_cloudwatch_log_group.api_tokens_safety_net,
  ]
}

resource "aws_cloudwatch_log_group" "api_tokens_safety_net" {
  name              = "/aws/lambda/${var.api_tokens_safety_net_name}"
  retention_in_days = 0
}

resource "aws_iam_policy" "api_tokens_safety_net" {
  name        = "${var.api_tokens_safety_net_name}-policy"
  path        = "/"
  description = "IAM policy for pull the credential report, and logging from the lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    },
    {
      "Sid": "Stmt1500330918000",
      "Effect": "Allow",
      "Action": [
          "iam:GenerateCredentialReport",
          "iam:GetCredentialReport"
      ],
      "Resource": [
          "*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
          "dynamodb:PutItem",
          "dynamodb:GetItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-2:${data.aws_caller_identity.current.account_id}:table/awsidtoken_table"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "api_tokens_safety_net" {
  role       = aws_iam_role.api_tokens_safety_net.name
  policy_arn = aws_iam_policy.api_tokens_safety_net.arn
}

resource "aws_cloudwatch_event_rule" "api_tokens_safety_net" {
    name = "every-4-5-hours"
    description = "Fires every 4.5 hours"
    schedule_expression = "rate(270 minutes)"
}

resource "aws_cloudwatch_event_target" "api_tokens_safety_net" {
    rule = "${aws_cloudwatch_event_rule.api_tokens_safety_net.name}"
    target_id = var.api_tokens_safety_net_name
    arn = "${aws_lambda_function.api_tokens_safety_net.arn}"
}
resource "aws_lambda_permission" "api_tokens_safety_net" {
   statement_id  = "AllowCloudWatchInvoke"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.api_tokens_safety_net.function_name
   principal     = "events.amazonaws.com"
   source_account = data.aws_caller_identity.current.account_id
   source_arn = "${aws_cloudwatch_event_rule.api_tokens_safety_net.arn}"
}
