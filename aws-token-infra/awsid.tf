terraform {
  backend "s3" {
    bucket = "terraformstate-<account_id>"
    key    = "terraformstate"
    region = "us-east-2"
    dynamodb_table = "terraformlock"
  }
}

variable "slack_webhook_url" {
  type = string
}

provider "aws" {
   region = "us-east-2"
}

data "aws_caller_identity" "current" {}

# CreateUserAPITokens
#
# AWS API Token creation infrastructure
#

variable "create_user_api_tokens_name" {
  default = "CreateUserAPITokens"
}

resource "aws_iam_role" "create_user_api_tokens" {
  name = "AWSTokenRole"

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

data "archive_file" "create_user_api_tokens_lambda" {
    type        = "zip"
    source_file  = "./lambdas/${var.create_user_api_tokens_name}/lambda_function.py"
    output_path = "./lambdas/${var.create_user_api_tokens_name}/lambda_function_payload.zip"
}

resource "aws_lambda_function" "create_user_api_tokens" {
  filename      = "./lambdas/${var.create_user_api_tokens_name}/lambda_function_payload.zip"
  function_name = var.create_user_api_tokens_name
  role          = aws_iam_role.create_user_api_tokens.arn
  handler       = "lambda_function.lambda_handler"
  source_code_hash = "${data.archive_file.create_user_api_tokens_lambda.output_base64sha256}"
  timeout       = 60

  runtime = "python3.9"

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }
  depends_on = [
    aws_iam_role_policy_attachment.create_user_api_tokens,
    aws_cloudwatch_log_group.create_user_api_tokens,
  ]
}

resource "aws_cloudwatch_log_group" "create_user_api_tokens" {
  name              = "/aws/lambda/${var.create_user_api_tokens_name}"
  retention_in_days = 14
}

# See also the following AWS managed policy: AWSLambdaBasicExecutionRole
resource "aws_iam_policy" "create_user_api_tokens" {
  name        = "lambda_logging"
  path        = "/"
  description = "IAM policy creating new users and logging from the lambda"

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
          "iam:CreateAccessKey",
          "iam:CreateUser",
          "iam:GetUser"
      ],
      "Resource": [
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
          "dynamodb:PutItem",
          "dynamodb:GetItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-2:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.awsidtoken_table.name}"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "create_user_api_tokens" {
  role       = aws_iam_role.create_user_api_tokens.name
  policy_arn = aws_iam_policy.create_user_api_tokens.arn
}

resource "aws_api_gateway_rest_api" "create_user_api_tokens" {
  name        = var.create_user_api_tokens_name
}

resource "aws_api_gateway_resource" "create_user_api_tokens" {
   rest_api_id = aws_api_gateway_rest_api.create_user_api_tokens.id
   parent_id   = aws_api_gateway_rest_api.create_user_api_tokens.root_resource_id
   path_part   = var.create_user_api_tokens_name
}

resource "aws_api_gateway_method" "create_user_api_tokens" {
   rest_api_id   = aws_api_gateway_rest_api.create_user_api_tokens.id
   resource_id   = aws_api_gateway_resource.create_user_api_tokens.id
   http_method   = "ANY"
   authorization = "NONE"
}

resource "aws_api_gateway_integration" "create_user_api_tokens" {
   rest_api_id = aws_api_gateway_rest_api.create_user_api_tokens.id
   resource_id = aws_api_gateway_method.create_user_api_tokens.resource_id
   http_method = aws_api_gateway_method.create_user_api_tokens.http_method

   integration_http_method = "POST"
   type                    = "AWS_PROXY"
   uri                     = aws_lambda_function.create_user_api_tokens.invoke_arn
}

resource "aws_api_gateway_method_response" "create_user_api_tokens" {
  rest_api_id = aws_api_gateway_rest_api.create_user_api_tokens.id
  resource_id = aws_api_gateway_resource.create_user_api_tokens.id
  http_method = aws_api_gateway_method.create_user_api_tokens.http_method
  status_code = "200"
}

resource "aws_api_gateway_deployment" "create_user_api_tokens" {
   depends_on = [
     aws_api_gateway_integration.create_user_api_tokens,
    #  aws_api_gateway_integration.lambda_root,
   ]

   rest_api_id = aws_api_gateway_rest_api.create_user_api_tokens.id
   stage_name  = "prod"
}
resource "aws_lambda_permission" "create_user_api_tokens" {
   statement_id  = "AllowAPIGatewayInvoke"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.create_user_api_tokens.function_name
   principal     = "apigateway.amazonaws.com"

   # The "/*/*" portion grants access from any method on any resource
   # within the API Gateway REST API.
   source_arn = "${aws_api_gateway_rest_api.create_user_api_tokens.execution_arn}/*/*"
}


output "base_url" {
  value = aws_api_gateway_deployment.create_user_api_tokens.invoke_url
}


# 
# Log storage
#

resource "aws_s3_bucket" "canarytoken_logs" {
  bucket        = "awskeytokentrailbucketall-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::awskeytokentrailbucketall-${data.aws_caller_identity.current.account_id}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::awskeytokentrailbucketall-${data.aws_caller_identity.current.account_id}/AWSLogs/${data.aws_caller_identity.current.account_id}/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
POLICY
}
resource "aws_cloudtrail" "canarytoken_logs" {
  name                          = "AWSKeyTokenTrailAll"
  s3_bucket_name                = aws_s3_bucket.canarytoken_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  s3_key_prefix                 = ""
  cloud_watch_logs_group_arn    = "${aws_cloudwatch_log_group.process_user_api_tokens_logs.arn}:*"
  cloud_watch_logs_role_arn     = aws_iam_role.process_user_api_tokens_logs_cloudtrail.arn
}

# ProcessUserAPITokensLogs
#
# AWS API Token alerting infrastructure
#

variable "process_user_api_tokens_logs" {
  default = "ProcessUserAPITokensLogs"
}

resource "aws_iam_role" "process_user_api_tokens_logs" {
  name = "AWSProcessTokenLogsRole"

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

data "archive_file" "process_user_api_tokens_logs_lambda" {
    type        = "zip"
    source_file  = "./lambdas/${var.process_user_api_tokens_logs}/lambda_function.py"
    output_path = "./lambdas/${var.process_user_api_tokens_logs}/lambda_function_payload.zip"
}

resource "aws_lambda_function" "process_user_api_tokens_logs" {
  filename      = "./lambdas/${var.process_user_api_tokens_logs}/lambda_function_payload.zip"
  function_name = var.process_user_api_tokens_logs
  role          = aws_iam_role.process_user_api_tokens_logs.arn
  handler       = "lambda_function.lambda_handler"
  source_code_hash = "${data.archive_file.process_user_api_tokens_logs_lambda.output_base64sha256}"
  timeout       = 60

  runtime = "python3.9"

  depends_on = [
    aws_iam_role_policy_attachment.process_user_api_tokens_logs,
    aws_cloudwatch_log_group.process_user_api_tokens_logs_lambda_logs,
  ]
}
resource "aws_lambda_permission" "process_user_api_tokens_logs" {
   statement_id  = "AllowCloudWatchInvoke"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.process_user_api_tokens_logs.function_name
   principal     = "logs.us-east-2.amazonaws.com"
   source_account = data.aws_caller_identity.current.account_id
   source_arn = "${aws_cloudwatch_log_group.process_user_api_tokens_logs.arn}:*"
}

resource "aws_cloudwatch_log_group" "process_user_api_tokens_logs_lambda_logs" {
  name              = "/aws/lambda/${var.process_user_api_tokens_logs}"
  retention_in_days = 14
}

resource "aws_iam_policy" "process_user_api_tokens_logs_lambda_logs" {
  name        = "${var.process_user_api_tokens_logs}-Lambda-Logs"
  path        = "/"
  description = "IAM policy for writing lambda logs"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
          "kms:Decrypt"
      ],
      "Resource": "*"
    },
      {
        "Effect": "Allow",
        "Action": [
            "dynamodb:PutItem",
            "dynamodb:GetItem"
        ],
        "Resource": "arn:aws:dynamodb:us-east-2:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.awsidtoken_table.name}"
      },
    {
        "Effect": "Allow",
        "Action": "logs:CreateLogGroup",
        "Resource": "arn:aws:logs:us-east-2:${data.aws_caller_identity.current.account_id}:*"
    },
    {
      "Effect": "Allow",
      "Action": [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
      ],
      "Resource": [
          "arn:aws:logs:us-east-2:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.process_user_api_tokens_logs}:*"
      ]
    }
  ]
}
EOF
}

resource "aws_iam_policy" "process_user_api_tokens_logs_cloudtrail" {
  name        = var.process_user_api_tokens_logs
  path        = "/"
  description = "IAM policy for writing logs streams"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
        {
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-2:${data.aws_caller_identity.current.account_id}:log-group:*",
      "Effect": "Allow"
    },
    {
        "Sid": "AWSCloudTrailCreateLogStream20141101",
        "Effect": "Allow",
        "Action": [
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ],
        "Resource": [
            "arn:aws:logs:us-east-2:${data.aws_caller_identity.current.account_id}:log-group:${aws_cloudwatch_log_group.process_user_api_tokens_logs.name}:log-stream:*"
        ]
    }
  ]
}
EOF
}
resource "aws_iam_role" "process_user_api_tokens_logs_cloudtrail" {
  name = "CloudTrail_CloudWatchLogs_Role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
resource "aws_iam_role_policy_attachment" "process_user_api_tokens_logs_cloudtrail" {
  role       = aws_iam_role.process_user_api_tokens_logs_cloudtrail.name
  policy_arn = aws_iam_policy.process_user_api_tokens_logs_cloudtrail.arn
}
resource "aws_iam_role_policy_attachment" "process_user_api_tokens_logs" {
  role       = aws_iam_role.process_user_api_tokens_logs.name
  policy_arn = aws_iam_policy.process_user_api_tokens_logs_lambda_logs.arn
}


resource "aws_cloudwatch_log_group" "process_user_api_tokens_logs" {
  name = "AWSKeyTokenAll"
  retention_in_days = 0
}

resource "aws_cloudwatch_log_subscription_filter" "process_user_api_tokens_logs" {
  name            = "LambdaStream_${var.process_user_api_tokens_logs}"
  log_group_name  = aws_cloudwatch_log_group.process_user_api_tokens_logs.name
  filter_pattern  = "{$.userIdentity.type = IAMUser}"
  destination_arn = aws_lambda_function.process_user_api_tokens_logs.arn
}


#
# Storage tables
#

resource "aws_dynamodb_table" "awsidtoken_table" {
  name           = "awsidtoken_table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "Username"

  attribute {
    name = "Username"
    type = "S"
  }
}

#
# Safety Net
#

variable "api_tokens_safety_net_name" {
  default = "APITokensSafetyNet"
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

data "archive_file" "api_tokens_safety_net_lambda" {
    type        = "zip"
    source_file  = "./lambdas/${var.api_tokens_safety_net_name}/lambda_function.py"
    output_path = "./lambdas/${var.api_tokens_safety_net_name}/lambda_function_payload.zip"
}

resource "aws_lambda_function" "api_tokens_safety_net" {
  filename      = "./lambdas/${var.api_tokens_safety_net_name}/lambda_function_payload.zip"
  function_name = var.api_tokens_safety_net_name
  role          = aws_iam_role.api_tokens_safety_net.arn
  handler       = "lambda_function.lambda_handler"
  source_code_hash = "${data.archive_file.api_tokens_safety_net_lambda.output_base64sha256}"
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
      "Resource": "arn:aws:dynamodb:us-east-2:${data.aws_caller_identity.current.account_id}:table/${aws_dynamodb_table.awsidtoken_table.name}"
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