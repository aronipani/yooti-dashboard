output "function_arns" {
  description = "Map of function key to Lambda ARN."
  value       = { for k, v in aws_lambda_function.this : k => v.arn }
}

output "function_names" {
  description = "Map of function key to Lambda function name."
  value       = { for k, v in aws_lambda_function.this : k => v.function_name }
}

output "invoke_arns" {
  description = "Map of function key to Lambda invoke ARN (for API Gateway integration)."
  value       = { for k, v in aws_lambda_function.this : k => v.invoke_arn }
}
