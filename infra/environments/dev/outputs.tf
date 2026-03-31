# Dev environment outputs.
# Used by deploy scripts and CI/CD workflows.

output "dynamodb_table_name" {
  description = "DynamoDB metrics table name."
  value       = module.dynamodb.table_name
}

output "api_url" {
  description = "API Gateway invoke URL."
  value       = module.api_gateway.api_url
}

output "cloudfront_domain" {
  description = "CloudFront distribution domain name."
  value       = module.frontend.distribution_domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID (for cache invalidation)."
  value       = module.frontend.distribution_id
}

output "s3_bucket_name" {
  description = "S3 frontend bucket name (for deploy script)."
  value       = module.frontend.bucket_name
}
