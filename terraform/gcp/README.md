# GCP Terraform Configuration

This directory contains Terraform configurations for deploying the Movies Big Data Pipeline infrastructure on Google Cloud Platform.

## Architecture

The infrastructure includes:

- **Cloud Storage Buckets**: Three separate buckets for bronze/silver/gold layers
- **Service Account**: Pipeline execution identity with appropriate permissions
- **Lifecycle Policies**: Automatic storage class transitions
- **Logging**: Cloud Logging integration for access logs
- **IAM**: Fine-grained access control

## Prerequisites

1. Google Cloud SDK installed and configured
2. Terraform >= 1.0 installed
3. GCP project with billing enabled
4. Appropriate IAM permissions

## Setup

### 1. Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Windows
# Download from: https://cloud.google.com/sdk/docs/install
```

### 2. Authenticate with GCP

```bash
gcloud auth login
gcloud auth application-default login
```

### 3. Set Project

```bash
# List projects
gcloud projects list

# Set active project
gcloud config set project YOUR_PROJECT_ID
```

### 4. Initialize Terraform

```bash
cd terraform/gcp
terraform init
```

### 5. Create terraform.tfvars

```bash
cat > terraform.tfvars <<EOF
project_id  = "your-gcp-project-id"
environment = "dev"
region      = "us-central1"
EOF
```

### 6. Review Plan

```bash
terraform plan
```

### 7. Apply Configuration

```bash
terraform apply
```

## Configuration

### Required Variables

- `project_id`: Your GCP project ID (required)

### Optional Variables

- `environment`: Deployment environment (default: "dev")
- `region`: GCP region (default: "us-central1")
- `project_name`: Project name (default: "movies-pipeline")
- `bucket_location`: Bucket location (default: "US")
- `storage_class`: Default storage class (default: "STANDARD")
- `enable_versioning`: Enable object versioning (default: true)
- `lifecycle_age_bronze`: Days before transitioning bronze data (default: 90)
- `lifecycle_age_silver`: Days before transitioning silver data (default: 180)

### Example terraform.tfvars

```hcl
project_id            = "my-gcp-project"
environment           = "production"
region                = "us-central1"
bucket_location       = "US"
storage_class         = "STANDARD"
lifecycle_age_bronze  = 60
lifecycle_age_silver  = 120
```

## Storage Classes and Lifecycle

GCP automatically transitions data through storage classes:

**Bronze Layer:**
- Standard → Nearline (after 90 days)
- Nearline → Coldline (after 180 days)
- Coldline → Archive (after 360 days)

**Silver Layer:**
- Standard → Nearline (after 180 days)
- Nearline → Coldline (after 360 days)

**Gold Layer:**
- Stays in Standard (frequently accessed)

**Storage Class Pricing (approximate):**
- Standard: $0.020/GB/month
- Nearline: $0.010/GB/month
- Coldline: $0.004/GB/month
- Archive: $0.0012/GB/month

## Usage

After deployment, configure your pipeline:

```bash
# Get bucket names
export GCP_BRONZE_BUCKET=$(terraform output -raw bronze_bucket_name)
export GCP_SILVER_BUCKET=$(terraform output -raw silver_bucket_name)
export GCP_GOLD_BUCKET=$(terraform output -raw gold_bucket_name)

# Get service account
export GCP_SERVICE_ACCOUNT=$(terraform output -raw service_account_email)
```

Update your `.env` file:

```
GCP_PROJECT_ID=your-project-id
GCP_BRONZE_BUCKET=movies-pipeline-dev-bronze
GCP_SILVER_BUCKET=movies-pipeline-dev-silver
GCP_GOLD_BUCKET=movies-pipeline-dev-gold
```

## Accessing Data

### Using gsutil

```bash
# List buckets
gsutil ls

# List objects in bucket
gsutil ls gs://movies-pipeline-dev-bronze/

# Upload file
gsutil cp data/movies.csv gs://movies-pipeline-dev-bronze/

# Download file
gsutil cp gs://movies-pipeline-dev-gold/analytics/yearly_stats.parquet ./output/

# Sync directory
gsutil -m rsync -r data/ gs://movies-pipeline-dev-bronze/
```

### Using Python SDK

```python
from google.cloud import storage

# Initialize client
client = storage.Client(project='your-project-id')

# Upload blob
bucket = client.bucket('movies-pipeline-dev-bronze')
blob = bucket.blob('movies.csv')
blob.upload_from_filename('data/movies.csv')

# Download blob
blob = bucket.blob('movies.csv')
blob.download_to_filename('output/movies.csv')
```

### Using gcloud CLI

```bash
# List objects
gcloud storage ls gs://movies-pipeline-dev-bronze/

# Copy file
gcloud storage cp data/movies.csv gs://movies-pipeline-dev-bronze/

# Copy directory
gcloud storage cp -r data/ gs://movies-pipeline-dev-bronze/
```

## Service Account

The pipeline service account has `storage.objectAdmin` role on all buckets.

### Create Service Account Key (for local development)

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=$(terraform output -raw service_account_email)

export GOOGLE_APPLICATION_CREDENTIALS="key.json"
```

**Security Note**: Never commit service account keys to Git!

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all buckets and data!

## State Management

For production environments, configure remote state backend:

```bash
# Create state bucket
gsutil mb gs://movies-pipeline-terraform-state

# Enable versioning
gsutil versioning set on gs://movies-pipeline-terraform-state
```

Then uncomment the backend configuration in `backend.tf`.

## Security

- Uniform bucket-level access (no ACLs)
- Private buckets (no public access)
- Object versioning enabled
- Service account with least privilege
- Encrypted at rest by default

## Cost Optimization

- Automatic lifecycle transitions to cheaper storage classes
- Log retention limited to 30 days
- Use Nearline/Coldline for infrequent access
- Consider multi-regional buckets for redundancy (but costs more)

## Monitoring

### View Access Logs

```bash
# View recent logs
gcloud logging read "resource.type=gcs_bucket" \
  --limit 50 \
  --format json

# View logs for specific bucket
gcloud logging read "resource.type=gcs_bucket AND resource.labels.bucket_name=movies-pipeline-dev-bronze" \
  --limit 50
```

### Monitor Storage Usage

```bash
# Get bucket size
gsutil du -sh gs://movies-pipeline-dev-bronze/

# Get object count
gsutil ls -r gs://movies-pipeline-dev-bronze/ | wc -l
```

### Cost Monitoring

```bash
# View billing
gcloud billing accounts list

# Export billing data
gcloud billing accounts get-iam-policy BILLING_ACCOUNT_ID
```

## Troubleshooting

### Permission Denied Errors

Ensure you have the following roles:
- `roles/storage.admin` or `roles/owner`
- `roles/iam.serviceAccountAdmin`
- `roles/resourcemanager.projectIamAdmin`

```bash
# Add roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:your-email@example.com" \
  --role="roles/storage.admin"
```

### API Not Enabled

```bash
# Enable required APIs
gcloud services enable storage.googleapis.com
gcloud services enable logging.googleapis.com
```

### Bucket Name Already Exists

Bucket names are globally unique. Change `project_name` in `terraform.tfvars`.

### Quota Exceeded

Check project quotas:

```bash
gcloud compute project-info describe --project=YOUR_PROJECT_ID
```

Request quota increase in Cloud Console if needed.

## Best Practices

1. **Use Service Accounts**: Don't use personal credentials for automation
2. **Enable Versioning**: Protect against accidental deletion
3. **Implement Lifecycle Policies**: Optimize costs
4. **Monitor Usage**: Set up billing alerts
5. **Use Labels**: Tag resources for cost tracking
6. **Separate Environments**: Use different projects for dev/staging/prod
7. **Backup Critical Data**: Export to different region or provider

## Integration with Pipeline

Update your Python code to use GCS:

```python
from google.cloud import storage

# Configure in settings
GCP_BRONZE_BUCKET = os.getenv("GCP_BRONZE_BUCKET")
GCP_SILVER_BUCKET = os.getenv("GCP_SILVER_BUCKET")
GCP_GOLD_BUCKET = os.getenv("GCP_GOLD_BUCKET")

# Use in repository
client = storage.Client()
bucket = client.bucket(GCP_BRONZE_BUCKET)
```

## Support

For issues, please check:

1. GCP project is active and has billing enabled
2. All required APIs are enabled
3. Service account has correct permissions
4. Bucket names are globally unique
5. Terraform version compatibility
6. Region supports all features

## Additional Resources

- [GCS Documentation](https://cloud.google.com/storage/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCS Pricing](https://cloud.google.com/storage/pricing)
- [Best Practices](https://cloud.google.com/storage/docs/best-practices)

