# Illustrative Terraform for Managed Identity and RBAC Reference

# 1. Create a User-Assigned Managed Identity
# This is recommended for modularity and better lifecycle management in IaC.
resource "azurerm_user_assigned_identity" "example" {
  name                = "id-example-processor"
  location            = var.location
  resource_group_name = var.resource_group_name
}

# 2. Assign a Least-Privilege Data Plane Role
# We assign 'Storage Blob Data Reader' at the scope of a specific container.
# This prevents broad access to the entire storage account.
resource "azurerm_role_assignment" "blob_reader" {
  scope                = var.target_storage_container_id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}

# 3. Configure an Azure Function to use the identity
# We use identity-based connection settings instead of connection strings.
resource "azurerm_linux_function_app" "example" {
  name                = "func-example-app"
  location            = var.location
  resource_group_name = var.resource_group_name
  # ... other required fields ...

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.example.id]
  }

  app_settings = {
    # Prefix 'STORAGE_CONNECTION' matches the name used in code
    "STORAGE_CONNECTION__accountName" = var.storage_account_name
    "STORAGE_CONNECTION__credential"  = "managedidentity"
    "STORAGE_CONNECTION__clientId"    = azurerm_user_assigned_identity.example.client_id
  }
}

# 4. Configure a Key Vault Access Policy (RBAC is preferred, but this shows identity use)
# RBAC is the recommended model for new Key Vaults.
resource "azurerm_role_assignment" "kv_secrets_user" {
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}
