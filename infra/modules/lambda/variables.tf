# Input variables for the Lambda module.

variable "project" {
  type        = string
  description = "Project name used in resource naming."
}

variable "environment" {
  type        = string
  description = "Deployment environment: dev, staging, or prod."

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "memory_size" {
  type        = number
  description = "Lambda memory in MB. Override per environment (e.g. 128 for dev, 256 for prod)."
  default     = 256
}

variable "timeout" {
  type        = number
  description = "Lambda timeout in seconds."
  default     = 30
}

variable "dynamodb_table_name" {
  type        = string
  description = "DynamoDB table name passed to Lambda env vars."
}

variable "dynamodb_table_arn" {
  type        = string
  description = "DynamoDB table ARN for IAM policy."
}

variable "gsi_arn" {
  type        = string
  description = "DynamoDB GSI-1 ARN for IAM policy."
}

variable "source_code_path" {
  type        = string
  description = "Path to the Lambda source code directory (services/api_python)."
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources."
  default     = {}
}
