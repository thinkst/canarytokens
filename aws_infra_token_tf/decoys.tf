resource "aws_s3_bucket" "fake-s3-buckets" {
  for_each      = contains(keys(local.decoy_config), "s3_bucket_names") ? toset(local.decoy_config.s3_bucket_names) : toset([])
  bucket        = each.value
  force_destroy = true
  depends_on    = [null_resource.account_id_validator]
}

# TODO: try depends on for first time upload
resource "aws_s3_object" "fake-s3-objects" {
  count      = contains(keys(local.decoy_config), "s3_objects") ? length(local.decoy_config.s3_objects) : 0
  bucket     = local.decoy_config.s3_objects[count.index].bucket
  key        = local.decoy_config.s3_objects[count.index].key
  content    = local.decoy_config.s3_objects[count.index].content
  depends_on = [aws_s3_bucket.fake-s3-buckets]
}

resource "aws_sqs_queue" "fake-sqs-queues" {
  for_each   = contains(keys(local.decoy_config), "sqs_queues") ? toset(local.decoy_config.sqs_queues) : toset([])
  name       = each.value
  depends_on = [null_resource.account_id_validator]
}

resource "aws_ssm_parameter" "fake-ssm-parameters" {
  for_each = contains(keys(local.decoy_config), "ssm_parameters") ? {
    for param in local.decoy_config.ssm_parameters :
    param.name => param
  } : {}
  name       = each.key
  type       = "String"
  value      = each.value.value
  depends_on = [null_resource.account_id_validator]
}

resource "aws_secretsmanager_secret" "fake-secrets" {
  for_each   = contains(keys(local.decoy_config), "secrets") ? toset(local.decoy_config.secrets) : toset([])
  name       = each.value
  depends_on = [null_resource.account_id_validator]
}

resource "aws_dynamodb_table" "fake-tables" {
  for_each     = contains(keys(local.decoy_config), "tables") ? toset(local.decoy_config.tables) : toset([])
  name         = each.value
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = local.default_dynamodb_hash_key

  attribute {
    name = local.default_dynamodb_hash_key
    type = "S"
  }
  depends_on = [null_resource.account_id_validator]
}
