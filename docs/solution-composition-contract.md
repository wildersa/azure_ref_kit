# Solution Composition Contract

This document defines the repository-wide contract for solutions located in the `solutions/` directory. It ensures that solutions are consistently described, packageable, and verifiable.

## Solution Statuses

A solution's status is defined in its `solution.yaml` and determines the level of required documentation and implementation.

| Status | Description | Requirements |
|--------|-------------|--------------|
| `scaffold` | Conceptual composition only. | `README.md`, `solution.yaml` |
| `partial` | Has runtime/package map but some blocks are mock/scaffold/future. | `README.md`, `solution.yaml`, `runtime-map.md`, `deploy/package-map.yaml` (optional) |
| `executable` | Validated runtime map, package map, infra outputs, package/deploy flow, and tests. | `README.md`, `solution.yaml`, `runtime-map.md`, `deploy/package-map.yaml`, `infra/terraform/`, `tests/` |

## Building Block Statuses

Building blocks referenced in a solution must have one of the following statuses:

- `implemented`: Runtime code and tests exist in `building-blocks/`.
- `mock`: A simplified version for testing or demo purposes.
- `scaffold`: Contract/shell only, no implementation.
- `future`: Planned but not yet started.
- `external`: Provided by a third party or existing Azure service not managed in this repo.

## Required Metadata (solution.yaml)

The `solution.yaml` file must declare the building blocks used and their operational metadata.

```yaml
name: solution-name
status: scaffold | partial | executable
purpose: Brief description of the customer scenario.
building_blocks:
  - id: block-id
    path: building-blocks/path/to/block
    role: worker | api | portal | observer | security
    status: implemented | mock | scaffold | future | external
    deploy_target: pipeline_function_app | api_function_app | portal | none
    entrypoint: app.py (optional)
```

## Runtime Map (runtime-map.md)

Required for `partial` and `executable` solutions. It must explain:

- Azure runtime targets in the solution.
- Which building blocks run in each target.
- Entrypoint per target.
- Contracts between blocks.
- Real vs mock/scaffold/future status.
- Local run flow.
- Package/deploy flow.
- Blockers preventing `executable` status.

## Package Map (deploy/package-map.yaml)

Required for `executable` solutions. It defines how source folders map to deployable artifacts.

```yaml
artifacts:
  - name: api_function_app
    type: azure_function
    sources:
      - building-blocks/hosting/webapp-agent-api
      - building-blocks/functions/portal-api-functions
  - name: portal
    type: static_web_app
    sources:
      - building-blocks/portals/static-status-portal
```

## Validation & Cataloging

- **Enforcement (`scripts/check_solution_composition.py`)**: Enforces the composition contract. It verifies that all declared paths exist and that mandatory files are present based on the solution's status.
- **Cataloging (`scripts/generate_catalog.py`)**: Automatically parses metadata from `module.yaml` and `solution.yaml` to generate the unified human-readable (`docs/catalog.md`) and LLM-ready (`docs/catalog.json`) catalog indexes. It also runs in validation mode (`--check`) during CI/CD to prevent out-of-sync pushes.

