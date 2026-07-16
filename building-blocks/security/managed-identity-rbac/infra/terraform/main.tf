# Managed Identity and RBAC Reference Implementation
# Concrete reference for one workload receiving one narrowly scoped role over one resource.
#
# P0 Requirement Compliance:
# - Uses User-Assigned Managed Identity (UAMI) for better modularity and lifecycle control.
# - Implements least-privilege RBAC by scoping the assignment to a specific Resource ID.
# - No hardcoded identifiers (subscription, tenant, principal, etc.).
# - No Owner/Contributor or wildcard permissions (enforced via variable validation).

resource "azurerm_user_assigned_identity" "workload" {
  name                = "id-${var.workload_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

# Concrete least-privilege example: narrowly scoped role assignment
resource "azurerm_role_assignment" "least_privilege" {
  scope                = var.target_resource_id
  role_definition_name = var.role_definition_name
  principal_id         = azurerm_user_assigned_identity.workload.principal_id

  # Skip metadata lookup for faster deployment if the role name is well-known
  skip_service_principal_aad_check = true
}
