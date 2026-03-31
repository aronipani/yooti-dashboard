output "parameter_arns" {
  description = "Map of parameter name to ARN (String parameters)."
  value       = { for k, v in aws_ssm_parameter.string : k => v.arn }
}

output "secure_parameter_arns" {
  description = "Map of parameter name to ARN (SecureString parameters)."
  value       = { for k, v in aws_ssm_parameter.secure : k => v.arn }
}

output "parameter_names" {
  description = "Map of parameter key to full SSM path."
  value = merge(
    { for k, v in aws_ssm_parameter.string : k => v.name },
    { for k, v in aws_ssm_parameter.secure : k => v.name },
  )
}
