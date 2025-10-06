# Resource Group
resource "azurerm_resource_group" "pipeline_rg" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location

  tags = {
    Project     = "movies-big-data-pipeline"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Storage Account
resource "azurerm_storage_account" "data_lake" {
  name                     = "${var.project_name}${var.environment}sa"
  resource_group_name      = azurerm_resource_group.pipeline_rg.name
  location                 = azurerm_resource_group.pipeline_rg.location
  account_tier             = var.account_tier
  account_replication_type = var.account_replication_type
  account_kind             = "StorageV2"
  is_hns_enabled           = true # Enable Data Lake Gen2

  blob_properties {
    versioning_enabled = var.enable_versioning

    delete_retention_policy {
      days = 7
    }

    container_delete_retention_policy {
      days = 7
    }
  }

  tags = {
    Project     = "movies-big-data-pipeline"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Blob Containers
resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.data_lake.name
  container_access_type = "private"
}

# Lifecycle Management Policy
resource "azurerm_storage_management_policy" "lifecycle_policy" {
  storage_account_id = azurerm_storage_account.data_lake.id

  rule {
    name    = "bronze-data-lifecycle"
    enabled = true

    filters {
      prefix_match = ["bronze/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        tier_to_cool_after_days_since_modification_greater_than    = 30
        tier_to_archive_after_days_since_modification_greater_than = 90
        delete_after_days_since_modification_greater_than          = var.lifecycle_delete_days
      }
    }
  }

  rule {
    name    = "silver-data-lifecycle"
    enabled = true

    filters {
      prefix_match = ["silver/"]
      blob_types   = ["blockBlob"]
    }

    actions {
      base_blob {
        tier_to_cool_after_days_since_modification_greater_than    = 60
        tier_to_archive_after_days_since_modification_greater_than = 180
        delete_after_days_since_modification_greater_than          = var.lifecycle_delete_days
      }
    }
  }
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "pipeline_logs" {
  name                = "${var.project_name}-${var.environment}-logs"
  location            = azurerm_resource_group.pipeline_rg.location
  resource_group_name = azurerm_resource_group.pipeline_rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = {
    Project     = "movies-big-data-pipeline"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Storage Account Diagnostics
resource "azurerm_monitor_diagnostic_setting" "storage_diagnostics" {
  name                       = "storage-diagnostics"
  target_resource_id         = "${azurerm_storage_account.data_lake.id}/blobServices/default"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.pipeline_logs.id

  enabled_log {
    category = "StorageRead"
  }

  enabled_log {
    category = "StorageWrite"
  }

  enabled_log {
    category = "StorageDelete"
  }

  metric {
    category = "Transaction"
    enabled  = true
  }
}

