# Managed Identity and RBAC Reference Pattern

Reference pattern for implementing least-privilege service-to-service authentication and authorization in Azure.

## Purpose

Managed identities eliminate the need for developers to manage credentials. This building block defines the standard for using identities and Role-Based Access Control (RBAC) to secure Azure resources without hardcoded secrets or broad permissions.

## Scenarios

- **Serverless Tools:** Azure Functions calling Blob Storage or AI Services.
- **Pipeline Orchestration:** Durable Functions managing state in Storage Tables/Blobs.
- **Agent Integration:** AI Foundry Agents accessing search indexes or tool APIs.
- **Modular Infrastructure:** Sharing a single identity across multiple related microservices.

## Identity Choice Guidance

| Type | Lifecycle | Sharing | Recommendation |
| :--- | :--- | :--- | :--- |
| **System-assigned** | Tied to the resource. | Cannot be shared. | Use for simple, single-resource workloads where the identity should die with the service. |
| **User-assigned** | Standalone resource. | Can be shared across resources. | **Recommended** for modularity, pre-authorization in IaC flows, and workloads spanning multiple resources (e.g., a Function App and a Web App sharing access). |

## RBAC Scope Guidance

Always assign roles at the **lowest possible scope** to minimize the "blast radius" of a compromised identity.

1. **Resource Scope (Best):** Assign the role directly on the specific Blob Container, Queue, or AI Project.
2. **Resource Group Scope (Good):** Assign at the RG level if the identity needs access to all resources of that type within the group.
3. **Subscription Scope (Avoid):** Only use if the identity must manage resources across the entire subscription (rare for runtime identities).

## Forbidden Practices

To maintain a secure environment, the following practices are strictly forbidden:

- **Wildcard Permissions:** Never use `*` or `Owner` roles for runtime identities.
- **Committed Secrets:** Do not commit API keys, connection strings, or service principal secrets to source control.
- **Hardcoded Identifiers:** Do not hardcode Tenant IDs, Subscription IDs, or Managed Identity Object IDs in application code.
- **Raw Token Exposure:** Do not log, store, or return raw Entra ID access tokens to client-facing interfaces.
- **Connection Strings:** Prefer identity-based connections over Shared Access Keys (SAK) or connection strings for supported services.

## Local Development Fallback

It is critical to separate the credentials used during local development from the identity used in the Azure runtime.

- **Local Development:** Developers use their own Entra ID identity (via Azure CLI, VS Code, or Azure PowerShell) or a dedicated local Service Principal. This identity typically has broader "Contributor" or "Developer" access to the development environment.
- **Azure Runtime:** The deployed service uses a **Managed Identity** with strictly limited **Data Plane** RBAC roles (e.g., `Storage Blob Data Reader`). The service should never use the developer's personal credentials or a broad-privilege service principal in production.

For a seamless transition, use the `DefaultAzureCredential` class from the `azure-identity` SDK, which handles the fallback logic automatically.

### Python Implementation
```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Use DefaultAzureCredential to automatically pick up the right identity
# (Azure CLI locally, Managed Identity in Azure)
credential = DefaultAzureCredential()

# Initialize client using identity, not a connection string
blob_service_client = BlobServiceClient(
    account_url="https://<account_name>.blob.core.windows.net",
    credential=credential
)
```

## Concrete Implementation Examples

### Example 1: Azure Function Accessing Blob Storage (Identity-Based)

In this pattern, the Function App is granted `Storage Blob Data Contributor` access to a specific storage account. No connection string is stored in App Settings.

**Infrastructure (Conceptual):**
1. User-Assigned Managed Identity: `id-storage-processor`
2. Role Assignment: `Storage Blob Data Contributor` assigned to `id-storage-processor` at the scope of `st-process-artifacts`.
3. Function App Setting: `STORAGE_CONNECTION__accountName = "stprocessartifacts"`

**Code:**
```python
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Azure Functions can use identity-based triggers and bindings
# For manual client initialization:
account_name = os.environ["STORAGE_CONNECTION__accountName"]
account_url = f"https://{account_name}.blob.core.windows.net"
client = BlobServiceClient(account_url, credential=DefaultAzureCredential())
```

### Example 2: AI Foundry Agent Tool Boundary

When an AI Foundry Agent calls a tool (e.g., an Azure Function), the Function should use its own Managed Identity to access backend data, ensuring the agent itself never touches raw data or secrets.

**Infrastructure (Conceptual):**
1. Agent Identity: `id-foundry-agent`
2. Tool Identity: `id-search-tool`
3. Role Assignment: `id-search-tool` is granted `Search Index Data Reader` on the AI Search index.
4. The Agent calls the Tool via an authenticated endpoint; the Tool then uses `id-search-tool` to perform the search.

**Code (Tool Side):**
```python
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

# The tool uses its own identity to perform the action
credential = DefaultAzureCredential()
search_client = SearchClient(endpoint, index_name, credential=credential)

def perform_search(query):
    # Returns only safe, business-level results to the Agent
    results = search_client.search(query)
    return sanitize_results(results)
```

## Architecture Flow

```mermaid
flowchart TD
    subgraph "Local Development"
        Dev[Developer/Runner] -->|az login / env| LocalCreds[Local Credentials\nAzure CLI / Service Principal]
    end

    subgraph "Azure Environment"
        Service[Azure Service\nFunctions/Web App] -->|Assigned| MI[Managed Identity\nSystem or User Assigned]
    end

    subgraph "Authorization"
        LocalCreds -->|DefaultAzureCredential| SDK[Azure SDK Client]
        MI -->|DefaultAzureCredential| SDK
        SDK -->|Request Token| Entra[Microsoft Entra ID]
        Entra -->|Issue Token| SDK
    end

    subgraph "Target Resource"
        SDK -->|Authorized Request| Resource[Target Resource\ne.g. Blob Storage]
        Role[RBAC Role Assignment\ne.g. Storage Blob Data Reader] -.->|Scopes Access| Resource
        MI -.->|Principal| Role
    end
```

## Azure Deployment Assumptions

- **Entra ID Integration:** The target resource must support Microsoft Entra authentication.
- **Identity Support:** The hosting platform (e.g., Azure Functions, ACA) must support Managed Identity.
- **RBAC Propagation:** Role assignments can take up to 10-15 minutes to propagate across all Azure regions.

## Known Limits

- **System-Assigned Limits:** A resource can only have one system-assigned identity.
- **User-Assigned Limits:** There are limits on the number of user-assigned identities per resource (typically 20-50).
- **Scope Limits:** Subscription-level role assignments are capped (typically 2000-4000 per subscription).

## Validation Notes

To verify this pattern in a new module:
1. Ensure `module.yaml` defines the required RBAC roles in the `security_boundary`.
2. Check that `DefaultAzureCredential` is used in the source code.
3. Verify that no secrets or connection strings are present in App Settings or environment variables.

## References

- [Managed identities for Azure resources overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Azure role-based access control (Azure RBAC) overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Azure RBAC best practices](https://learn.microsoft.com/en-us/azure/role-based-access-control/best-practices)
- [Azure built-in roles](https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles)
- [Azure Functions identity-based connections](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference?tabs=blob&pivots=programming-language-python#configure-an-identity-based-connection)
