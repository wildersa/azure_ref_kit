resource "azurerm_storage_account" "artifact_store" {
  name                     = "${var.prefix}artifacts${random_id.storage_suffix.hex}"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Secure defaults
  https_only_enabled            = true
  min_tls_version                = "TLS1_2"
  public_network_access_enabled  = true # Enable but restrict via network_rules
  shared_access_key_enabled      = false # Prefer Entra/RBAC

  network_rules {
    default_action = "Deny"
    ip_rules       = var.allowed_ips
    bypass         = ["AzureServices", "Logging", "Metrics"]
  }

  blob_properties {
    delete_retention_policy {
      days = 7
    }
    container_delete_retention_policy {
      days = 7
    }
  }

  tags = {
    environment = "reference"
    module      = "blob-artifact-store"
  }
}

resource "azurerm_storage_container" "artifacts" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.artifact_store.name
  container_access_type = "private" # No public access
}

resource "random_id" "storage_suffix" {
  byte_length = 4
}

resource "azurerm_role_assignment" "storage_blob_data_owner_runtime" {
  count                = var.runtime_principal_id != null ? 1 : 0
  scope                = azurerm_storage_account.artifact_store.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = var.runtime_principal_id
}

# Explicitly separate management plane and data plane.
# Deployment principal gets management access only.
resource "azurerm_role_assignment" "storage_account_contributor_deployer" {
  scope                = azurerm_storage_account.artifact_store.id
  role_definition_name = "Storage Account Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

data "azurerm_client_config" "current" {}
