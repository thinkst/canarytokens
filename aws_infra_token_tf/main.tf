data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  decoy_config              = jsondecode(file("${path.module}/decoy_vars.json"))
  expected_account_id       = lookup(local.decoy_config, "account_id", null)
  expected_region           = lookup(local.decoy_config, "region", null)
  default_dynamodb_hash_key = "id"

  safe_s3_bucket_names = lookup(local.decoy_config, "s3_bucket_names", [])
  safe_s3_objects      = lookup(local.decoy_config, "s3_objects", [])
  safe_sqs_queues      = lookup(local.decoy_config, "sqs_queues", [])
  safe_ssm_parameters  = lookup(local.decoy_config, "ssm_parameters", [])
  safe_secrets         = lookup(local.decoy_config, "secrets", [])
  safe_tables          = lookup(local.decoy_config, "tables", [])
  safe_table_items     = lookup(local.decoy_config, "table_items", [])
}

# Validate account ID check and exit if it's false
resource "null_resource" "account_id_validator" {
  lifecycle {
    precondition {
      condition     = data.aws_caller_identity.current.account_id == local.expected_account_id
      error_message = "AWS account ID validation failed. Expected: ${local.expected_account_id}, Got: ${data.aws_caller_identity.current.account_id}"
    }
  }
}

# Validate region check and exit if it's false
resource "null_resource" "region_validator" {
  lifecycle {
    precondition {
      condition     = data.aws_region.current.name == local.expected_region
      error_message = "You're trying to create decoys in ${data.aws_region.current.name}, but this Terraform targets ${local.expected_region} specifically. You can set the AWS_REGION variable to switch your region: export AWS_REGION=${local.expected_region}, then run 'terraform apply' again."
    }
  }
}

provider "aws" {
  region = local.expected_region
}
