# AWS Terraform Configuration

This directory contains Terraform configurations for deploying the Movies Big Data Pipeline infrastructure on AWS.

## Architecture

The infrastructure includes:

- **S3 Data Lake**: Three-tier storage (bronze/silver/gold)
- **IAM Roles**: Pipeline execution role with S3 access
- **CloudWatch Logs**: Centralized logging
- **Lifecycle Policies**: Automatic data archiving to Glacier

## Prerequisites

1. AWS CLI installed and configured
2. Terraform >= 1.0 installed
3. AWS credentials with appropriate permissions

## Setup

### 1. Configure AWS Credentials

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 2. Initialize Terraform

```bash
cd terraform/aws
terraform init
```

### 3. Review Plan

```bash
terraform plan
```

### 4. Apply Configuration

```bash
terraform apply
```

## Configuration

### Variables

Edit `terraform.tfvars` or pass variables via command line:

```bash
terraform apply -var="environment=prod" -var="aws_region=us-west-2"
```

Available variables:

- `environment`: Deployment environment (default: "dev")
- `aws_region`: AWS region (default: "us-east-1")
- `project_name`: Project name (default: "movies-pipeline")
- `enable_versioning`: Enable S3 versioning (default: true)
- `enable_encryption`: Enable S3 encryption (default: true)
- `lifecycle_days_bronze`: Days before archiving bronze data (default: 90)
- `lifecycle_days_silver`: Days before archiving silver data (default: 180)

### Example terraform.tfvars

```hcl
environment           = "production"
aws_region            = "us-east-1"
enable_versioning     = true
lifecycle_days_bronze = 60
lifecycle_days_silver = 120
```

## Usage

After deployment, configure your pipeline to use the S3 bucket:

```bash
export AWS_S3_BUCKET=$(terraform output -raw s3_bucket_name)
```

Update your `.env` file:

```
AWS_S3_BUCKET=movies-pipeline-dev-data-lake
AWS_REGION=us-east-1
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all data in the S3 bucket!

## State Management

For production environments, configure remote state backend (uncomment in `backend.tf`):

```bash
# Create state bucket and DynamoDB table first
aws s3 mb s3://movies-pipeline-terraform-state
aws dynamodb create-table \
  --table-name movies-pipeline-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## Security

- All S3 buckets have public access blocked
- Server-side encryption enabled by default
- IAM roles follow least privilege principle
- Versioning enabled for data recovery

## Cost Optimization

- Automatic lifecycle transitions to Glacier
- CloudWatch log retention limited to 14 days
- Consider using S3 Intelligent-Tiering for frequently accessed data

## Monitoring

View logs in CloudWatch:

```bash
aws logs tail /aws/pipeline/movies-pipeline-dev --follow
```

## Support

For issues, please check:

1. AWS credentials are configured correctly
2. IAM user has required permissions
3. Terraform version compatibility
4. Region availability for services

