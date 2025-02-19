variable "ticket_service_url" {
  type = string
}

variable "ticket_service_recipient" {
  type = string
}

variable "zendesk_exposed_ticket_tag" {
  type = string
}

variable "zendesk_closed_ticket_tag" {
  type = string
}

variable "zendesk_assignee" {
  type = string
}

variable "zendesk_auth_secret_id" {
  type = string
}

variable "tokens_servers_allow_list" {
  type = string
}

variable "tokens_post_url_override" {
  type    = string
  default = null
}
