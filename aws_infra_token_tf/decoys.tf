resource "aws_s3_bucket" "fake-s3-buckets" {
  for_each      = toset(local.safe_s3_bucket_names)
  bucket        = each.value
  force_destroy = true
  depends_on    = [null_resource.account_id_validator, null_resource.region_validator]
}

resource "aws_s3_object" "fake-s3-objects" {
  count      = length(local.safe_s3_objects)
  bucket     = local.safe_s3_objects[count.index].bucket
  key        = local.safe_s3_objects[count.index].key
  content    = local.safe_s3_objects[count.index].content
  depends_on = [aws_s3_bucket.fake-s3-buckets]
}

resource "aws_sqs_queue" "fake-sqs-queues" {
  for_each   = toset(local.safe_sqs_queues)
  name       = each.value
  depends_on = [null_resource.account_id_validator, null_resource.region_validator]
}

resource "aws_ssm_parameter" "fake-ssm-parameters" {
  for_each = {
    for param in local.safe_ssm_parameters :
    param.name => param
  }
  name       = each.key
  type       = "String"
  value      = each.value.value
  depends_on = [null_resource.account_id_validator, null_resource.region_validator]
}

resource "aws_secretsmanager_secret" "fake-secrets" {
  for_each   = toset(local.safe_secrets)
  name       = each.value
  depends_on = [null_resource.account_id_validator, null_resource.region_validator]
}

resource "aws_dynamodb_table" "fake-tables" {
  for_each     = toset(local.safe_tables)
  name         = each.value
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = local.default_dynamodb_hash_key

  attribute {
    name = local.default_dynamodb_hash_key
    type = "S"
  }
  depends_on = [null_resource.account_id_validator, null_resource.region_validator]
}

resource "aws_dynamodb_table_item" "fake-table-items" {
  for_each   = { for item in local.safe_table_items : "${item.table_name}-${item.key}-${item.value}" => item }
  table_name = each.value.table_name
  hash_key   = each.value.key # Assuming 'key' in table_items corresponds to the table's hash_key name

  item = jsonencode({
    (each.value.key) = { "S" = each.value.value }
  })

  depends_on = [aws_dynamodb_table.fake-tables]
}

resource "null_resource" "decoys_anchor" {
  depends_on = [
    aws_s3_object.fake-s3-objects,
    aws_sqs_queue.fake-sqs-queues,
    aws_ssm_parameter.fake-ssm-parameters,
    aws_secretsmanager_secret.fake-secrets,
    aws_dynamodb_table_item.fake-table-items,
  ]
}
