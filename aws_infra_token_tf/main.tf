data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  decoy_config = jsondecode(file("${path.module}/decoy_vars.json"))
  # Check if account_id exists in decoy_config, if not this should fail during plan/apply
  expected_account_id       = lookup(local.decoy_config, "account_id", null)
  expected_region           = lookup(local.decoy_config, "region", null)
  default_dynamodb_hash_key = "id"
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
      error_message = "AWS region validation failed. Expected: ${local.expected_region}, Got: ${data.aws_region.current.name}"
    }
  }
}
