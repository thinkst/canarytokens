terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      ManagedBy = "terraform"
      Project   = "aws-s3-bucket-cfn-infra"
    }
  }
}

variable "region" {
  description = "AWS region for the template bucket"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket that hosts the CFN template"
  type        = string
}

resource "aws_s3_bucket" "cfn_templates" {
  bucket        = var.bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "cfn_templates" {
  bucket = aws_s3_bucket.cfn_templates.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "cfn_templates" {
  bucket     = aws_s3_bucket.cfn_templates.id
  depends_on = [aws_s3_bucket_public_access_block.cfn_templates]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowCloudFormationRead"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.cfn_templates.arn}/*"
        Condition = {
          "ForAllValues:StringEquals" = {
            "aws:CalledVia" = "cloudformation.amazonaws.com"
          }
          Null = {
            "aws:CalledVia" = "false"
          }
        }
      }
    ]
  })
}

resource "aws_s3_object" "template" {
  bucket       = aws_s3_bucket.cfn_templates.id
  key          = "template.json"
  source       = "${path.module}/template.json"
  content_type = "application/json"
  etag         = filemd5("${path.module}/template.json")
}

output "template_url" {
  description = "frontend.env variable for AWS S3 bucket CFN template URL"
  value       = "CANARY_AWS_S3_BUCKET_CFN_TEMPLATE_URL=https://s3.${var.region}.amazonaws.com/${aws_s3_bucket.cfn_templates.id}/template.json"
}
