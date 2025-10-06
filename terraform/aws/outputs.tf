output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.data_lake.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.data_lake.arn
}

output "s3_bucket_region" {
  description = "Region of the S3 bucket"
  value       = aws_s3_bucket.data_lake.region
}

output "pipeline_role_arn" {
  description = "ARN of the pipeline IAM role"
  value       = aws_iam_role.pipeline_role.arn
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.pipeline_logs.name
}

