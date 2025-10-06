output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.pipeline_rg.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = azurerm_storage_account.data_lake.name
}

output "storage_account_primary_access_key" {
  description = "Primary access key for the storage account"
  value       = azurerm_storage_account.data_lake.primary_access_key
  sensitive   = true
}

output "storage_account_primary_connection_string" {
  description = "Primary connection string for the storage account"
  value       = azurerm_storage_account.data_lake.primary_connection_string
  sensitive   = true
}

output "bronze_container_name" {
  description = "Name of the bronze container"
  value       = azurerm_storage_container.bronze.name
}

output "silver_container_name" {
  description = "Name of the silver container"
  value       = azurerm_storage_container.silver.name
}

output "gold_container_name" {
  description = "Name of the gold container"
  value       = azurerm_storage_container.gold.name
}

output "log_analytics_workspace_id" {
  description = "ID of the Log Analytics workspace"
  value       = azurerm_log_analytics_workspace.pipeline_logs.id
}

