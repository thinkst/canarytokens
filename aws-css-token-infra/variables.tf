variable "aws_region" {
  type        = string
  description = "AWS region used to manage the CloudFront resources."
}

variable "function_name" {
  type        = string
  description = "Name of the existing CSS token CloudFront Function."
}

variable "function_comment" {
  type        = string
  description = "Comment configured on the existing CSS token CloudFront Function."
}

variable "key_value_store_name" {
  type        = string
  description = "Name of the existing CloudFront KeyValueStore containing CSS token referer exclusions."
}

variable "key_value_store_comment" {
  type        = string
  description = "Comment configured on the existing CloudFront KeyValueStore."
}

variable "publish" {
  type        = bool
  default     = false
  description = "Publish the DEVELOPMENT Function code to LIVE."
}

variable "alarm_actions" {
  type        = list(string)
  default     = []
  description = "SNS topic ARNs to notify when the CSS token CloudFront Function has execution errors."
}

variable "distribution_id" {
  type        = string
  description = "ID of the CloudFront distribution serving CSS token requests."
}

variable "function_error_alarm_name" {
  type        = string
  description = "Name of the existing CloudWatch alarm for function execution errors."
}

variable "function_error_alarm_function_name" {
  type        = string
  description = "CloudFront Function name currently monitored by the function error alarm."
}

variable "http_5xx_alarm_name" {
  type        = string
  description = "Name of the existing CloudWatch alarm for the distribution HTTP 5XX response rate."
}
