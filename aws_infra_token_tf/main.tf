data "aws_caller_identity" "current" {}

locals {
  decoy_config = jsondecode(file("${path.module}/decoy_vars.json"))
  # Check if account_id exists in decoy_config, if not this should fail during plan/apply
  expected_account_id       = lookup(local.decoy_config, "account_id", null)
  account_id_valid          = local.expected_account_id != null ? data.aws_caller_identity.current.account_id == local.expected_account_id : true
  account_id_check          = local.account_id_valid ? true : false
  default_dynamodb_hash_key = "id"
}

# Validate account ID check and exit if it's false
resource "null_resource" "account_id_validator" {
  lifecycle {
    precondition {
      condition     = local.account_id_check
      error_message = "AWS account ID validation failed. Expected: ${local.expected_account_id}, Got: ${data.aws_caller_identity.current.account_id}"
    }
  }
}
