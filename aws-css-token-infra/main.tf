resource "aws_cloudfront_key_value_store" "exclusions" {
  name    = var.key_value_store_name
  comment = var.key_value_store_comment

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_cloudfront_function" "this" {
  name                         = var.function_name
  runtime                      = "cloudfront-js-2.0"
  code                         = replace(file("${path.module}/CSSClonedSiteCFFunc/index.js"), "KVS_ID", aws_cloudfront_key_value_store.exclusions.id)
  comment                      = var.function_comment
  publish                      = var.publish
  key_value_store_associations = [aws_cloudfront_key_value_store.exclusions.arn]

  lifecycle {
    prevent_destroy = true
  }
}
