# Managed Identity and RBAC Reference Implementation

This directory contains a concrete reference for implementing least-privilege identity and RBAC using Terraform.

## Usage

This module is designed to be used as a reference or as a starting point for your own infrastructure. It creates a User-Assigned Managed Identity and assigns a built-in role to it over a target resource.

### Prerequisites

- An existing target resource (e.g., a Storage Account or Blob Container) to which the identity will be granted access.

### Inputs

| Name | Type | Description |
| :--- | :--- | :--- |
| `workload_name` | `string` | Name of the workload, used for naming the identity. |
| `location` | `string` | Azure region for the identity. |
| `resource_group_name` | `string` | Resource group where the identity will be created. |
| `target_resource_id` | `string` | Fully qualified Azure ID of the target resource (e.g., `/subscriptions/.../resourceGroups/.../providers/Microsoft.Storage/storageAccounts/.../blobServices/default/containers/mycontainer`). |
| `role_definition_name` | `string` | Built-in role name (e.g., `Storage Blob Data Reader`). |

### Outputs

| Name | Description |
| :--- | :--- |
| `identity_principal_id` | The Principal ID (Object ID) of the identity. |
| `identity_client_id` | The Client ID of the identity (used in application code). |
| `role_assignment_id` | The ID of the RBAC assignment. |

## Least-Privilege Implementation

- **Resource-level scope:** The role is assigned directly to the `target_resource_id`.
- **Built-in Data Plane role:** Only specific roles like `Storage Blob Data Reader` are recommended.
- **No secrets:** No connection strings or account keys are used or generated.
