# Infrastructure: Customer-Safe Status Boundary

This directory contains the Terraform/OpenTofu definitions for the customer-safe status boundary.

## Deployment/IaC Decision

**Status:** No-resource policy block.

This building block is primarily a security policy and data boundary contract. It does not own or provision standalone Azure resources because the boundary is implemented across other components (Foundry Agents, Azure Functions, and Portals).

Instead of deploying resources, this module's Terraform structure:
1.  **Defines the Policy:** Encapsulates the "Allowed" and "Forbidden" fields in a machine-readable `locals` block.
2.  **Provides a Reference:** Serves as a prerequisite and contract for other modules that *do* deploy resources.

By keeping this module provider-free and resource-free, we preserve the architectural intent as a pure policy boundary.

## Usage in Other Modules

When building a module that implements this boundary (e.g., a Portal API), you should:
-   Reference the policy defined in `main.tf`.
-   Use the `boundary_policy` output to validate or configure enforcement points.

## Validation

Since this module contains only metadata and no resources, validation is limited to HCL syntax and logical consistency.

```bash
# Example validation (if terraform is available)
terraform init -backend=false
terraform validate
```
