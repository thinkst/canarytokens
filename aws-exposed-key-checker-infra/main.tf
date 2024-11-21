locals {
  lambda_timeout = 120
  lambda_runtime = "python3.10"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.58"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket         = "aws-exposed-key-checker-infra-tfstate-frcebvb1wabk"
    key            = "terraform/state.tfstate"
    region         = "us-east-1"
    dynamodb_table = "aws-exposed-key-checker-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = "us-east-1"
}

# DB
resource "aws_dynamodb_table" "processed_table" {
  name                        = "ExposedKeyCheckerProcessed"
  billing_mode                = "PAY_PER_REQUEST"
  hash_key                    = "IamUser"
  deletion_protection_enabled = true

  attribute {
    name = "IamUser"
    type = "S"
  }
}

# Lambda
resource "null_resource" "pip_install" {
  triggers = {
    shell_hash = "${sha256(file("${path.module}/requirements.txt"))}"

    # Rebuild if directory is empty (ignoring .gitignore which is always there). Use a timestamp since we always want empty to trigger, not only when changing from not_empty
    empty_check = "${chomp(join("", [for file in fileset("${path.module}/layer/python", "*") : file != ".gitignore" ? "not_empty" : ""])) == "" ? timestamp() : "not_empty"}"
  }

  provisioner "local-exec" {
    command = "python3 -m pip install -r requirements.txt -t ${path.module}/layer/python"
  }
}

data "archive_file" "dependencies_layer_archive" {
  type        = "zip"
  source_dir  = "${path.module}/layer"
  output_path = "${path.module}/lambda_outputs/layer.zip"
  depends_on  = [null_resource.pip_install]
}

resource "aws_lambda_layer_version" "dependencies_layer" {
  layer_name          = "exposed-key-checker-dependencies"
  filename            = data.archive_file.dependencies_layer_archive.output_path
  source_code_hash    = data.archive_file.dependencies_layer_archive.output_base64sha256
  compatible_runtimes = ["python3.10"]
}

data "archive_file" "code_archive" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_source"
  output_path = "${path.module}/lambda_outputs/lambda_exposed_aws_key_checker_payload.zip"
}

resource "aws_lambda_function" "key_checker_lambda" {
  function_name    = "exposed_key_checker_lambda"
  handler          = "exposed_key_checker.lambda_handler.lambda_handler"
  runtime          = local.lambda_runtime
  timeout          = local.lambda_timeout
  filename         = data.archive_file.code_archive.output_path
  source_code_hash = data.archive_file.code_archive.output_base64sha256
  role             = aws_iam_role.key_checker_lambda_exec.arn
  layers           = [aws_lambda_layer_version.dependencies_layer.arn]

  environment {
    variables = merge(
      {
        TICKET_SERVICE_URL         = "${var.ticket_service_url}"
        TICKET_SERVICE_RECIPIENT   = "${var.ticket_service_recipient}"
        ZENDESK_EXPOSED_TICKET_TAG = "${var.zendesk_exposed_ticket_tag}"
        ZENDESK_AUTH_SECRET_ID     = "${var.zendesk_auth_secret_id}"
        TOKENS_SERVERS_ALLOW_LIST  = "${var.tokens_servers_allow_list}"
      },
      var.tokens_post_url_override != null ? { TOKENS_POST_URL_OVERRIDE = var.tokens_post_url_override } : {}
    )
  }
}

# IAM
resource "aws_iam_role" "key_checker_lambda_exec" {
  name = "exposed_key_checker_lambda_exec_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement : [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "key_checker_lambda_exec_policy" {
  name        = "exposed_key_checker_lambda_exec_role_policy"
  description = "AWS IAM Policy for the Exposed Key Checker"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "arn:aws:logs:*:*:*",
        "Effect" : "Allow"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "secretsmanager:GetSecretValue"
        ],
        "Resource" : [
          "${aws_secretsmanager_secret.zendesk_auth_data_secret.id}"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "dynamodb:PutItem",
          "dynamodb:Query",
        ],
        "Resource" : [
          "${aws_dynamodb_table.processed_table.arn}"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "console_event_dispatcher_lambda_basic_execution" {
  role       = aws_iam_role.key_checker_lambda_exec.name
  policy_arn = aws_iam_policy.key_checker_lambda_exec_policy.arn
}

# Schedule lambda run
resource "aws_cloudwatch_event_rule" "periodic_run" {
  name                = "run_exposed_key_checker_periodically"
  schedule_expression = "rate(12 hours)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.periodic_run.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.key_checker_lambda.arn
}

resource "aws_lambda_permission" "allow_eventbridge_periodic" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.key_checker_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.periodic_run.arn
}

# Secrets

# This secret value is added manually
resource "aws_secretsmanager_secret" "zendesk_auth_data_secret" {
  name = var.zendesk_auth_secret_id
}

# TF state
resource "aws_s3_bucket" "terraform_state" {
  bucket = "aws-exposed-key-checker-infra-tfstate-frcebvb1wabk"
  tags = {
    Name = "Terraform State Bucket for aws-exposed-key-checker"
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "terraform_state_lock" {
  name         = "aws-exposed-key-checker-tf-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name = "Terraform Lock Table for aws-exposed-key-checker"
  }
}
