# Terraform / OpenTofu deployment requirement

Every Azure-deployable module or solution in this repository must have an explicit deployment/IaC decision.

## Default folder shape

When a module or solution creates or depends on Azure resources, use this folder under that module or solution:

```text
infra/
  terraform/
    README.md
    main.tf
    variables.tf
    outputs.tf
```

`versions.tf` may be added when provider constraints are useful.

## Required behavior

- Keep Terraform/OpenTofu local to the module or solution being changed.
- Use current Microsoft Learn docs before adding Azure resource assumptions.
- Prefer small, validateable deployment references over production-grade infrastructure.
- Do not create fake resources only to fill files.
- Do not commit Terraform state, plans, secrets, `.env`, `local.settings.json`, connection strings, customer IDs, tenant IDs, subscription IDs, or real org identifiers.
- If the component is not deployable yet, include a short `Deployment/IaC decision` in the PR body and avoid speculative infrastructure.

## Validation

Use the smallest applicable validation:

```bash
terraform fmt -check -recursive <module-or-solution>/infra/terraform
terraform init -backend=false <module-or-solution>/infra/terraform
terraform validate <module-or-solution>/infra/terraform
```

If Terraform/OpenTofu is unavailable in the execution environment, the PR body must say so and include manual HCL validation by inspection.

## Reference

- Terraform on Azure overview: https://learn.microsoft.com/en-us/azure/developer/terraform/overview
