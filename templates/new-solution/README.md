# New Solution

## Scenario

Describe the customer/process scenario.

## Architecture Diagram

```mermaid
flowchart LR
  User[Customer/User] --> Portal[Static Web Apps portal]
  Portal --> API[Azure Functions API]
  API --> Agent[Foundry Agent]
  API --> Pipeline[Pipeline or DevOps status tool]
  Pipeline --> Observability[Application Insights / Azure Monitor]
```

## Composed Blocks

- TBD (list from `building-blocks/`)

## Entrypoints

- **Manual**: TBD
- **Automatic**: TBD

## Customer Outcome

- TBD

## Deployment Assumptions

- TBD

## Local/Demo Flow

- TBD
