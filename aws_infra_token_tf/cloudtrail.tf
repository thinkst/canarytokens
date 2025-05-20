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

resource "aws_cloudtrail" "trail" {
  name           = "trail-${random_string.trail_name.result}"
  s3_bucket_name = aws_s3_bucket.trail_bucket.id
  s3_key_prefix  = local.decoy_config.canarytoken_id

  depends_on = [
    null_resource.account_id_validator,
    aws_s3_bucket.trail_bucket,
    aws_dynamodb_table.fake-tables,
    aws_s3_bucket.fake-s3-buckets,
    aws_s3_object.fake-s3-objects,
    aws_sqs_queue.fake-sqs-queues,
  ]

  dynamic "advanced_event_selector" {
    for_each = contains(keys(local.decoy_config), "s3_bucket_names") ? [1] : []
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
    for_each = contains(keys(local.decoy_config), "sqs_queues") ? [1] : []
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
    for_each = contains(keys(local.decoy_config), "tables") ? [1] : []
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
