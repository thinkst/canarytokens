locals {
  has_s3_resources       = length(local.safe_s3_bucket_names) > 0 && length(aws_s3_bucket.fake-s3-buckets) > 0
  has_sqs_resources      = length(local.safe_sqs_queues) > 0 && length(aws_sqs_queue.fake-sqs-queues) > 0
  has_dynamodb_resources = length(local.safe_tables) > 0 && length(aws_dynamodb_table.fake-tables) > 0

  has_resources_to_monitor = local.has_s3_resources || local.has_sqs_resources || local.has_dynamodb_resources

  s3_pattern = length(local.safe_s3_bucket_names) > 0 ? {
    detail = {
      requestParameters = {
        bucketName = local.safe_s3_bucket_names
      }
    }
  } : null

  sqs_name_pattern = length(local.safe_sqs_queues) > 0 ? {
    detail = {
      requestParameters = {
        queueName = local.safe_sqs_queues
      }
    }
  } : null

  sqs_url_pattern = length(local.safe_sqs_queues) > 0 ? {
    detail = {
      requestParameters = {
        queueUrl = [for queue in aws_sqs_queue.fake-sqs-queues : queue.url]
      }
    }
  } : null

  dynamodb_pattern = length(local.safe_tables) > 0 ? {
    detail = {
      requestParameters = {
        tableName = local.safe_tables
      }
    }
  } : null

  secrets_pattern = length(local.safe_secrets) > 0 ? {
    detail = {
      requestParameters = {
        secretId = concat(
          local.safe_secrets,
          [for secret in aws_secretsmanager_secret.fake-secrets : secret.arn]
        )
      }
    }
  } : null

  ssm_pattern = length(local.safe_ssm_parameters) > 0 ? {
    source = ["aws.ssm"]
    detail = {
      resources = {
        ARN = [for param in aws_ssm_parameter.fake-ssm-parameters : param.arn]
      }
    }
  } : null

  patterns = [
    local.s3_pattern,
    local.sqs_name_pattern,
    local.sqs_url_pattern,
    local.dynamodb_pattern,
    local.secrets_pattern,
    local.ssm_pattern
  ]

  valid_patterns = [for pattern in local.patterns : pattern if pattern != null]

  event_pattern = length(local.valid_patterns) == 0 ? "{}" : (
    length(local.valid_patterns) == 1 ? jsonencode(local.valid_patterns[0]) : jsonencode({ "$or" = local.valid_patterns })
  )
}

resource "aws_cloudwatch_event_rule" "decoy_events" {
  count         = length(local.valid_patterns) > 0 ? 1 : 0
  name          = "trail-events-${local.decoy_config.canarytoken_id}"
  description   = "Match events for trail analysis"
  event_pattern = local.event_pattern
  state         = "ENABLED_WITH_ALL_CLOUDTRAIL_MANAGEMENT_EVENTS"
  depends_on    = [null_resource.account_id_validator, null_resource.region_validator, null_resource.decoys_anchor]
}

data "aws_iam_policy_document" "eventbridge_assume_role" {
  count = length(local.valid_patterns) > 0 ? 1 : 0
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "aws:SourceArn"
      values   = [aws_cloudwatch_event_rule.decoy_events[0].arn]
    }
  }
}

data "aws_iam_policy_document" "eventbridge_target_policy" {
  count = length(local.valid_patterns) > 0 ? 1 : 0
  statement {
    effect = "Allow"
    actions = [
      "events:PutEvents"
    ]
    resources = [local.decoy_config.target_bus_arn]
  }
}

resource "aws_iam_role" "eventbridge_target_role" {
  count              = length(local.valid_patterns) > 0 ? 1 : 0
  name               = "eventbridge-target-role-${random_string.trail_name.result}"
  assume_role_policy = data.aws_iam_policy_document.eventbridge_assume_role[0].json
}

resource "aws_iam_role_policy" "eventbridge_target_policy" {
  count  = length(local.valid_patterns) > 0 ? 1 : 0
  name   = "eventbridge-target-policy-${random_string.trail_name.result}"
  role   = aws_iam_role.eventbridge_target_role[0].id
  policy = data.aws_iam_policy_document.eventbridge_target_policy[0].json
}

resource "aws_cloudwatch_event_target" "decoy_events_target" {
  count     = length(local.valid_patterns) > 0 ? 1 : 0
  rule      = aws_cloudwatch_event_rule.decoy_events[0].name
  target_id = "TrailAnalysisBus"
  arn       = local.decoy_config.target_bus_arn
  role_arn  = aws_iam_role.eventbridge_target_role[0].arn
}

resource "random_string" "trail_name" {
  length  = 16
  lower   = true
  numeric = true
  upper   = false
  special = false
}

resource "aws_s3_bucket" "trail_bucket" {
  bucket        = "trail-bucket-${random_string.trail_name.result}"
  force_destroy = true
  depends_on    = [aws_cloudwatch_event_target.decoy_events_target, null_resource.decoys_anchor]
}

data "aws_iam_policy_document" "trail_bucket_policy" {
  statement {
    sid    = "AWSCloudTrailAclCheck"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.trail_bucket.arn]
  }

  statement {
    sid    = "AWSCloudTrailWrite"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.trail_bucket.arn}/*"]

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

resource "aws_s3_bucket_policy" "trail_bucket_policy" {
  bucket = aws_s3_bucket.trail_bucket.id
  policy = data.aws_iam_policy_document.trail_bucket_policy.json
}

resource "aws_cloudtrail" "trail_with_data_events" {
  count          = local.has_resources_to_monitor ? 1 : 0
  name           = "trail-${random_string.trail_name.result}"
  s3_bucket_name = aws_s3_bucket.trail_bucket.id
  s3_key_prefix  = local.decoy_config.canarytoken_id

  include_global_service_events = true
  enable_logging                = true
  is_multi_region_trail         = false

  depends_on = [aws_s3_bucket.trail_bucket, null_resource.decoys_anchor]

  dynamic "advanced_event_selector" {
    for_each = local.has_s3_resources ? [1] : []
    content {
      name = "S3 objects"

      field_selector {
        field  = "eventCategory"
        equals = ["Data"]
      }

      field_selector {
        field  = "resources.type"
        equals = ["AWS::S3::Object"]
      }

      field_selector {
        field       = "resources.ARN"
        starts_with = formatlist("%s/", [for bucket in aws_s3_bucket.fake-s3-buckets : bucket.arn])
      }
    }
  }

  dynamic "advanced_event_selector" {
    for_each = local.has_sqs_resources ? [1] : []
    content {
      name = "SQS queues"

      field_selector {
        field  = "eventCategory"
        equals = ["Data"]
      }

      field_selector {
        field  = "resources.type"
        equals = ["AWS::SQS::Queue"]
      }

      field_selector {
        field       = "resources.ARN"
        starts_with = [for queue in aws_sqs_queue.fake-sqs-queues : queue.arn]
      }
    }
  }

  dynamic "advanced_event_selector" {
    for_each = local.has_dynamodb_resources ? [1] : []
    content {
      name = "DynamoDB tables"

      field_selector {
        field  = "eventCategory"
        equals = ["Data"]
      }

      field_selector {
        field  = "resources.type"
        equals = ["AWS::DynamoDB::Table"]
      }

      field_selector {
        field       = "resources.ARN"
        starts_with = [for table in aws_dynamodb_table.fake-tables : table.arn]
      }
    }
  }
}

# Basic CloudTrail without advanced event selectors - created when we don't have S3, SQS, DynamoDB Tables
resource "aws_cloudtrail" "trail_management_only" {
  count          = local.has_resources_to_monitor ? 0 : 1
  name           = "trail-${random_string.trail_name.result}"
  s3_bucket_name = aws_s3_bucket.trail_bucket.id
  s3_key_prefix  = local.decoy_config.canarytoken_id

  include_global_service_events = true
  enable_logging                = true
  is_multi_region_trail         = false

  depends_on = [aws_s3_bucket.trail_bucket, null_resource.decoys_anchor]
}
