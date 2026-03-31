# Input variables for the API Gateway module.
# Populated by DASH-013-T002.

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

variable "lambda_invoke_arns" {
  type        = map(string)
  description = "Map of function name to invoke ARN for Lambda proxy integrations."
}

variable "lambda_function_names" {
  type        = map(string)
  description = "Map of function name to function name for API Gateway permissions."
}

variable "cors_origins" {
  type        = string
  description = "Allowed CORS origin (e.g. http://localhost:5173 or CloudFront URL)."
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to all resources."
  default     = {}
}
