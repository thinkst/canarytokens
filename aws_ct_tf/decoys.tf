locals {
  decoy_config = jsondecode(file("${path.module}/decoy_vars.json"))
}

resource "aws_s3_bucket" "fake-s3-buckets" {
  for_each      = toset(local.decoy_config.s3_bucket_names)
  bucket        = each.value
  force_destroy = true

  tags = {
    Name = "fake"
  }
}

# TODO: try depends on for first time upload
resource "aws_s3_object" "fake-s3-objects" {
  count   = length(local.decoy_config.s3_objects)
  bucket  = local.decoy_config.s3_objects[count.index].bucket
  key     = local.decoy_config.s3_objects[count.index].key
  content = local.decoy_config.s3_objects[count.index].content
}
