# Infrastructure: Customer-Safe Status Boundary

This directory contains the Terraform/OpenTofu definitions for the customer-safe status boundary.

## Deployment/IaC Decision

**Status:** No-resource policy block.

This building block is primarily a security policy and data boundary contract. It does not own or provision standalone Azure resources (like a specific database or API) because the boundary is implemented *across* other components (Foundry Agents, Azure Functions, and Portals).

Instead of deploying resources, this module's Terraform structure:
1.  **Defines the Policy:** Encapsulates the "Allowed" and "Forbidden" fields in a machine-readable `locals` block.
2.  **Provides a Reference:** Serves as a prerequisite and contract for other modules that *do* deploy resources.
3.  **Future-Proofs:** Provides the structure for future policy-as-code implementations (e.g., Azure Policy definitions or App Configuration entries) if they become necessary.

## Usage in Other Modules

When building a module that implements this boundary (e.g., a Portal API), you should:
-   Reference the policy defined in `main.tf`.
-   Ensure that any Application Insights, Storage, or Function resources are configured to prevent the leakage of "Forbidden Fields."
-   Use the `boundary_policy` output to validate or configure enforcement points.

## Validation

Since this module contains only metadata and no resources, validation is limited to HCL syntax and logical consistency.

```bash
# Example validation (if terraform is available)
terraform init -backend=false
terraform validate
```
