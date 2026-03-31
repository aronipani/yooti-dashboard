output "bucket_name" {
  description = "Name of the S3 frontend bucket."
  value       = aws_s3_bucket.frontend.id
}

output "bucket_arn" {
  description = "ARN of the S3 frontend bucket."
  value       = aws_s3_bucket.frontend.arn
}

output "distribution_id" {
  description = "ID of the CloudFront distribution."
  value       = aws_cloudfront_distribution.frontend.id
}

output "distribution_domain_name" {
  description = "Domain name of the CloudFront distribution."
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "distribution_arn" {
  description = "ARN of the CloudFront distribution."
  value       = aws_cloudfront_distribution.frontend.arn
}

output "oac_id" {
  description = "ID of the CloudFront Origin Access Control."
  value       = aws_cloudfront_origin_access_control.frontend.id
}
