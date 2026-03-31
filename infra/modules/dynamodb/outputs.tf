output "table_name" {
  description = "Name of the DynamoDB metrics table."
  value       = aws_dynamodb_table.metrics.name
}

output "table_arn" {
  description = "ARN of the DynamoDB metrics table."
  value       = aws_dynamodb_table.metrics.arn
}

output "table_id" {
  description = "ID of the DynamoDB metrics table."
  value       = aws_dynamodb_table.metrics.id
}

output "gsi_1_arn" {
  description = "ARN of GSI-1 (project_id + updated_at)."
  value       = "${aws_dynamodb_table.metrics.arn}/index/GSI-1"
}
