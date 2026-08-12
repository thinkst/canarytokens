variable "aws_region" {
  type        = string
  description = "AWS region in which to create the Terraform state bucket."
}

variable "bucket_name" {
  type        = string
  description = "Globally unique name for the Terraform state bucket."
}
