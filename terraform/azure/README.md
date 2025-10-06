# Azure Terraform Configuration

This directory contains Terraform configurations for deploying the Movies Big Data Pipeline infrastructure on Azure.

## Architecture

The infrastructure includes:

- **Resource Group**: Container for all resources
- **Storage Account**: Data Lake Gen2 with hierarchical namespace
- **Blob Containers**: Three-tier storage (bronze/silver/gold)
- **Lifecycle Management**: Automatic tiering and archiving
- **Log Analytics**: Centralized logging and monitoring
- **Diagnostics**: Storage account metrics and logs

## Prerequisites

1. Azure CLI installed and configured
2. Terraform >= 1.0 installed
3. Azure subscription with appropriate permissions

## Setup

### 1. Login to Azure

```bash
az login
```

Set subscription (if you have multiple):

```bash
az account set --subscription "Your Subscription Name"
```

### 2. Initialize Terraform

```bash
cd terraform/azure
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
terraform apply -var="environment=prod" -var="location=West US"
```

Available variables:

- `environment`: Deployment environment (default: "dev")
- `location`: Azure region (default: "East US")
- `project_name`: Project name (default: "moviespipeline")
- `enable_versioning`: Enable blob versioning (default: true)
- `account_tier`: Storage account tier (default: "Standard")
- `account_replication_type`: Replication type (default: "LRS")
- `lifecycle_delete_days`: Days before deleting old data (default: 365)

### Example terraform.tfvars

```hcl
environment              = "production"
location                 = "East US"
account_tier             = "Standard"
account_replication_type = "GRS"
lifecycle_delete_days    = 730
```

## Storage Tiers

The lifecycle policy automatically transitions data:

**Bronze Layer:**
- Cool tier: After 30 days
- Archive tier: After 90 days
- Delete: After 365 days (configurable)

**Silver Layer:**
- Cool tier: After 60 days
- Archive tier: After 180 days
- Delete: After 365 days (configurable)

**Gold Layer:**
- No automatic transitions (kept in hot tier)

## Usage

After deployment, configure your pipeline:

```bash
# Get storage account name
export AZURE_STORAGE_ACCOUNT=$(terraform output -raw storage_account_name)

# Get access key
export AZURE_STORAGE_KEY=$(terraform output -raw storage_account_primary_access_key)
```

Update your `.env` file:

```
AZURE_STORAGE_ACCOUNT=moviespipelinedevsa
AZURE_RESOURCE_GROUP=moviespipeline-dev-rg
```

## Data Lake Gen2 Features

This configuration enables Azure Data Lake Storage Gen2:

- **Hierarchical Namespace**: File system semantics
- **Better Performance**: Optimized for big data analytics
- **ACL Support**: Fine-grained access control
- **Compatible**: Works with Hadoop, Spark, and Azure services

## Accessing Data

### Using Azure CLI

```bash
# List containers
az storage container list --account-name <storage-account-name>

# Upload file
az storage blob upload \
  --account-name <storage-account-name> \
  --container-name bronze \
  --name movies.csv \
  --file data/movies.csv

# Download file
az storage blob download \
  --account-name <storage-account-name> \
  --container-name gold \
  --name analytics/yearly_stats.parquet \
  --file output/yearly_stats.parquet
```

### Using Python SDK

```python
from azure.storage.blob import BlobServiceClient

connection_string = "your-connection-string"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Upload blob
blob_client = blob_service_client.get_blob_client(
    container="bronze", 
    blob="movies.csv"
)
with open("data/movies.csv", "rb") as data:
    blob_client.upload_blob(data)
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will delete all data in the storage account!

## State Management

For production environments, configure remote state backend:

```bash
# Create resource group for state
az group create --name terraform-state-rg --location "East US"

# Create storage account for state
az storage account create \
  --name moviespipelinetfstate \
  --resource-group terraform-state-rg \
  --location "East US" \
  --sku Standard_LRS

# Create container
az storage container create \
  --name tfstate \
  --account-name moviespipelinetfstate
```

Then uncomment the backend configuration in `backend.tf`.

## Security

- Private containers (no public access)
- Blob versioning enabled for data recovery
- Soft delete enabled (7 days retention)
- Encryption at rest by default
- Diagnostic logging enabled

## Cost Optimization

- Automatic tiering to Cool/Archive storage
- LRS replication for development (consider GRS for production)
- Lifecycle policies to delete old data
- Log retention limited to 30 days

## Monitoring

View logs in Azure Portal or using CLI:

```bash
# Query Log Analytics
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "StorageBlobLogs | take 100"
```

## Troubleshooting

### Authentication Issues

```bash
# Check current account
az account show

# Re-login if needed
az login
```

### Permission Errors

Ensure your account has:
- Contributor role on subscription/resource group
- Storage Account Contributor role

### Storage Account Name Conflicts

Storage account names must be globally unique. If you get a conflict, change `project_name` in variables.

## Support

For issues, please check:

1. Azure CLI is logged in
2. Subscription is active and has quota
3. Storage account name is globally unique
4. Region supports all features
5. Terraform version compatibility

