resource "aws_s3_bucket" "fake-s3-buckets" {
  for_each      = toset(local.decoy_config.s3_bucket_names)
  bucket        = each.value
  force_destroy = true
  depends_on    = [null_resource.account_id_validator]
}

# TODO: try depends on for first time upload
resource "aws_s3_object" "fake-s3-objects" {
  count      = length(local.decoy_config.s3_objects)
  bucket     = local.decoy_config.s3_objects[count.index].bucket
  key        = local.decoy_config.s3_objects[count.index].key
  content    = local.decoy_config.s3_objects[count.index].content
  depends_on = [aws_s3_bucket.fake-s3-buckets]
}

resource "aws_sqs_queue" "fake-sqs-queues" {
  for_each   = toset(local.decoy_config.sqs_queues)
  name       = each.value
  depends_on = [null_resource.account_id_validator]
}

resource "aws_ssm_parameter" "fake-ssm-parameters" {
  for_each = {
    for param in local.decoy_config.ssm_parameters :
    param.name => param
  }
  name       = each.key
  type       = "String"
  value      = each.value.value
  depends_on = [null_resource.account_id_validator]
}

resource "aws_secretsmanager_secret" "fake-secrets" {
  for_each   = toset(local.decoy_config.secrets)
  name       = each.value
  depends_on = [null_resource.account_id_validator]
}

resource "aws_dynamodb_table" "fake-tables" {
  for_each     = toset(local.decoy_config.tables)
  name         = each.value
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = local.default_dynamodb_hash_key

  attribute {
    name = local.default_dynamodb_hash_key
    type = "S"
  }
  depends_on = [null_resource.account_id_validator]
}
