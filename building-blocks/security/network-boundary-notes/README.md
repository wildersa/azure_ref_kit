# Network Boundary Notes

## Purpose
Practical network boundary notes for customer-facing APIs, agents, tools, and Azure services. This module provides guidance on implementing network isolation in Azure solutions while maintaining architectural minimalism and security-first principles.

## Service-Level Mermaid Diagram
This diagram shows the logical separation between the public edge, the API boundary, and internal Azure services, highlighting the public vs. private trust zones.

```mermaid
flowchart TD
    subgraph PublicZone [Public / Edge Zone - Untrusted]
        User([Customer / Portal])
    end

    subgraph APIBoundary [API Boundary - Restricted Ingress]
        API[Portal API / Functions]
    end

    subgraph InternalZone [Internal / Private Zone - Trusted]
        subgraph VNet [Virtual Network]
            direction TB
            PE[Private Endpoints]
            Subnet[Integration Subnet]
        end

        Workers[Internal Workers / Orchestrators]
        Agent[Foundry Agent]
        Tools[Agent Tools / MCP]
        Storage[(Storage / Artifacts)]
        KV[Key Vault]
        AI[AI Foundry Services]
        Logs[App Insights / Logs]
    end

    User -->|HTTPS / WAF| API
    API -->|VNet Integration| Subnet
    Subnet -->|Private Link| PE
    PE --- Workers
    PE --- Agent
    PE --- Tools
    PE --- Storage
    PE --- KV
    PE --- AI
    PE --- Logs
```

## Boundary Model
The solution follows a multi-tier boundary model:
1.  **Public Edge**: Untrusted traffic from the internet.
2.  **Restricted Ingress Boundary**: Controlled entry point for APIs.
3.  **Internal Private Boundary**: Backend services isolated within a Virtual Network.

### Customer-Facing / API Separation Notes
The customer-facing portal (e.g., Static Web App) must be strictly separated from the backend API and internal state.
- The portal only interacts with the **Restricted Ingress** endpoint.
- All technical details, raw logs, and internal identifiers are redacted at the API boundary.
- For more details on data-level separation, see [Customer-Safe Status Boundary](../customer-safe-status-boundary/).

## Restricted Ingress Guidance
Public-facing services (like Azure Functions or App Service) must be protected against direct unauthorized access:
- **Access Restrictions**: Use IP filtering or Azure Service Tags to allow traffic only from trusted sources (e.g., Azure Front Door, Application Gateway, or the specific Static Web App).
- **Service Tags**: Prefer `AppService.Subnet` or `AzureStaticWebApps` tags where appropriate to simplify rule management.
- **WAF**: Deploy a Web Application Firewall (WAF) to provide Layer 7 protection.

## Private Endpoint Notes
Use Private Endpoints to bring PaaS services into your private network:
- **Private Link**: Ensures traffic between your compute and services (Storage, Key Vault, AI) never traverses the public internet.
- **DNS Resolution**: Ensure that internal DNS (Azure Private DNS Zones) is configured to resolve service FQDNs to their private endpoint IPs.
- **Sub-resources**: Remember to create private endpoints for each required sub-resource (e.g., `blob`, `queue`, `table` for a single storage account).

## Forbidden Exposures
To maintain a secure customer-facing surface, the following technical details must **NEVER** be exposed:
- **Raw Provider Payloads**: Untransformed responses from OpenAI, Azure AI, or DevOps APIs.
- **Raw Logs and Stack Traces**: Internal execution details, file paths, or line numbers.
- **Prompts and System Instructions**: Model grounding text or few-shot examples.
- **Secrets and Tokens**: API keys, SAS URLs, or bearer tokens.
- **Admin Endpoints**: Management interfaces or technical debugging paths (e.g., `/scm` or `/kudu`).
- **Internal Resource IDs**: Subscription IDs, Tenant IDs, or raw ARM URIs.
- **Unrestricted Write APIs**: Direct, unvalidated access to backend data modification.

## Concrete Examples

### 1. Static Web App to Functions API Boundary
- **Entry Point**: A Static Web App (SWA) frontend.
- **API Access**: Backend Azure Functions linked to the SWA.
- **Access Restriction**: Function App configured to only allow traffic from the SWA's linked backend mechanism.

### 2. Functions API to Private Backend Service Boundary
- **Compute**: Azure Functions (Flex Consumption) with VNet integration.
- **Integration Subnet**: Dedicated subnet delegated to `Microsoft.App/environments` (required for Flex Consumption VNet integration).
- **Private Endpoint**: Storage account with `public_network_access_enabled = false` and a Private Endpoint in the VNet.

## When to Use It

| Feature | Use Case | Recommendation |
| :--- | :--- | :--- |
| **Restricted Ingress** | Protecting public APIs | Always use for any service with a public IP. |
| **Private Endpoints** | Securing PaaS services | Use for Storage, Key Vault, AI Services in production. |
| **VNet Integration** | Compute-to-VNet access | Required for serverless compute reaching Private Endpoints. |

## Validation Notes
- **Design Review**: Verify network diagrams show the API boundary and private zones.
- **Compliance Check**: Ensure `public_network_access_enabled = false` for all backend PaaS in IaC.
- **Network Testing**: Verify that backend resources are inaccessible from outside the VNet.

## Deployment/IaC Decision
**No-IaC**: This module is documentation/pattern-only. Implementation is deferred to concrete reference solutions to avoid speculative infrastructure.

## Production-Grade Infrastructure Note
This reference describes logical isolation and is **not** a full Enterprise Landing Zone (ELZ). It does not implement Hub-Spoke, Centralized Firewalls, or global DNS management.

## References
- [Azure Private Endpoint overview](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)
- [App Service access restrictions](https://learn.microsoft.com/en-us/azure/app-service/overview-access-restrictions)
- [Azure Functions networking options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [Azure Storage network security](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security)
