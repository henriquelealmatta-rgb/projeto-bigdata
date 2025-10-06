# S3 Bucket for data storage
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-${var.environment}-data-lake"

  tags = {
    Name = "${var.project_name}-data-lake"
  }
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

# S3 Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket public access block
resource "aws_s3_bucket_public_access_block" "data_lake_public_access_block" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket folders (prefixes)
resource "aws_s3_object" "bronze_folder" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "bronze/"
}

resource "aws_s3_object" "silver_folder" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "silver/"
}

resource "aws_s3_object" "gold_folder" {
  bucket = aws_s3_bucket.data_lake.id
  key    = "gold/"
}

# Lifecycle policy for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "data_lake_lifecycle" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    id     = "bronze-data-transition"
    status = "Enabled"

    filter {
      prefix = "bronze/"
    }

    transition {
      days          = var.lifecycle_days_bronze
      storage_class = "GLACIER"
    }
  }

  rule {
    id     = "silver-data-transition"
    status = "Enabled"

    filter {
      prefix = "silver/"
    }

    transition {
      days          = var.lifecycle_days_silver
      storage_class = "GLACIER"
    }
  }
}

# IAM Role for pipeline execution
resource "aws_iam_role" "pipeline_role" {
  name = "${var.project_name}-${var.environment}-pipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for S3 access
resource "aws_iam_role_policy" "pipeline_s3_policy" {
  name = "${var.project_name}-s3-access"
  role = aws_iam_role.pipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "pipeline_logs" {
  name              = "/aws/pipeline/${var.project_name}-${var.environment}"
  retention_in_days = 14
}

