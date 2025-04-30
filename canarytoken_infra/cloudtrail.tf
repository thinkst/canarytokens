resource "aws_cloudtrail" "cloudtrail" {
  name           = local.decoy_config.cloudtrail_name
  s3_bucket_name = local.decoy_config.cloudtrail_destination_bucket
  s3_key_prefix  = local.decoy_config.canarytoken_id

  dynamic "advanced_event_selector" {
    for_each = aws_s3_bucket.fake-s3-buckets
    content {
      name = "s3 bucket events"
      field_selector {
        field  = "eventCategory"
        equals = ["Data"]
      }

      field_selector {
        field       = "resources.ARN"
        starts_with = ["${advanced_event_selector.value.arn}/"]
      }

      field_selector {
        field  = "resources.type"
        equals = ["AWS::S3::Object"]
      }
    }
  }
}
