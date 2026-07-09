# Infrastructure Reference: Managed Identity and RBAC

This building block is a **Security Reference Pattern** and does not manage standalone Azure resources directly.

## Deployment/IaC Decision

To prevent state management overhead for a pattern-only reference, no standalone Terraform modules are provided. Instead, use the illustrative HCL patterns below to implement these security standards in your specific solution or building block.

## Illustrative Terraform Patterns

These patterns demonstrate the implementation of least-privilege identity and RBAC.

### 1. User-Assigned Managed Identity
Recommended for modularity and better lifecycle management.

```hcl
resource "azurerm_user_assigned_identity" "example" {
  name                = "id-example-processor"
  location            = var.location
  resource_group_name = var.resource_group_name
}
```

### 2. Least-Privilege Data Plane Role Assignment
Assign roles at the narrowest possible scope (e.g., a specific container).

```hcl
resource "azurerm_role_assignment" "blob_reader" {
  scope                = var.target_storage_container_id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_user_assigned_identity.example.principal_id
}
```

### 3. Identity-Based Connection for Azure Functions
Configuring the service to use its identity instead of connection strings.

```hcl
resource "azurerm_linux_function_app" "example" {
  # ... existing configuration ...

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
```

## Validation

When implementing these patterns:
- Verify that `DefaultAzureCredential` is used in the source code.
- Ensure the role assignment scope is as narrow as possible.
- Confirm that no secrets are committed to configuration.
