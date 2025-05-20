resource "aws_cloudtrail" "trail" {
  name           = local.decoy_config.cloudtrail_name
  s3_bucket_name = local.decoy_config.cloudtrail_destination_bucket
  s3_key_prefix  = local.decoy_config.canarytoken_id

  depends_on = [
    null_resource.account_id_validator,
    aws_dynamodb_table.fake-tables,
    aws_s3_bucket.fake-s3-buckets,
    aws_s3_object.fake-s3-objects,
    aws_sqs_queue.fake-sqs-queues,
  ]

  # S3 bucket selector
  advanced_event_selector {
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

  # SQS queue selector
  advanced_event_selector {
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

  # DynamoDB table selector
  advanced_event_selector {
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
