# Infrastructure Reference: Managed Identity and RBAC

This directory provides illustrative Terraform patterns for implementing least-privilege identity and RBAC in Azure.

## Deployment/IaC Decision

This module is a **reference pattern** and does not own standalone Azure resources directly. It is intended to be used as a guide for other modules (e.g., Functions, Web Apps) that need to provision their own infrastructure securely.

## Patterns Demonstrated

- **User-Assigned Identity:** Recommended for modularity and pre-authorization.
- **Least-Privilege RBAC:** Data-plane role assignments at the narrowest possible scope.
- **Identity-Based Connections:** Configuring App Service/Functions to use identity instead of connection strings.

## Usage

Do not deploy this directory directly. Instead, copy the patterns into the `infra/terraform/` directory of your specific building block or solution.
