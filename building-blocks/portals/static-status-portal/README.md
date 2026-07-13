# Static Status Portal Shell

A minimal, locally testable, and customer-safe status portal shell for Azure Static Web Apps.

## Purpose

The Static Status Portal provides a read-only, business-level view of pipeline runs and outcomes. It implements the [Static Status Portal Contract](./README_CONTRACT.md) and enforces the [Customer-Safe Status Boundary](../../security/customer-safe-status-boundary/README.md).

This shell is designed to be hosted as an Azure Static Web App, consuming a controlled API that returns only allowlisted fields.

## Portal Responsibilities

- **Authentication & Authorization:** Leverages Azure Static Web Apps built-in auth to ensure users only see their own data.
- **Presentation:** Provides a clean, React-based interface for tracking pipeline progress.
- **Sanitization:** Implements client-side defense-in-depth to prevent any technical leakage.
- **Mocking:** Supports a local fixture mode for rapid development and testing.

## Architecture Boundary

```mermaid
flowchart LR
    Source[Internal Status Source] -->|Safe Status| Boundary[Customer-Safe Status Boundary]
    Boundary -->|Redact/Sanitize| Func[Controlled Functions API]
    Func -->|REST API| SWA[Static Web Apps Shell]
    SWA -->|HTTPS| Customer[Customer Browser]

    subgraph "Static Web Apps Portal"
        UI[React UI]
        Adapter[API Adapter + Defense-in-Depth Sanitizer]
        UI <--> Adapter
    end
```

## UI Surface Contract

The portal shell must provide the following functional components:

### 1. Run List
Displays a list of recent pipeline runs associated with the customer.
- **Fields:** Opaque ID, Status, Created Date, Summary.
- **Constraint:** Must never display internal database keys or subscription identifiers.

### 2. Run Detail & Timeline
A detailed view of a single pipeline run showing its execution path.
- **Behavior:** Renders high-level stages and their completion status.
- **Constraint:** Forbidden to show raw logs, internal step IDs, or technical stack traces.

### 3. Artifacts List
Lists safe, customer-facing artifacts produced by the pipeline.
- **Fields:** Friendly Name, Type, Size.
- **Constraint:** Must never expose SAS tokens, storage account keys, or internal storage paths (storage_ref).

### 4. Cost Summary
Optional high-level cost or resource consumption summary.
- **Behavior:** Shows business-level units (e.g., "Credits used").
- **Constraint:** Must never show raw Azure billing details or currency unless explicitly safe.

### 5. Friendly Error Panel
A dedicated UI component for rendering non-technical failures.
- **Behavior:** Translates technical error codes into human-readable guidance.
- **Constraint:** Must never render provider payloads, internal exceptions, or stack traces.

### 6. Start Run Placeholder
A UI shell for future pipeline triggers.
- **Behavior:** Currently read-only in this reference.

## API Contract Usage

The portal consumes the `CustomerSafeStatus` schema. All interactions with the backend are brokered through the API adapter which enforces the safety boundary.

## Customer-Safe Status Boundary

This module strictly adheres to the repository security standards.

### Forbidden Data (Internal-Only)
The following information is strictly forbidden from being displayed in the UI or contained in the API responses reaching the portal:
- **Raw Logs** and technical debug output.
- **Prompts** used for AI grounding or system instructions.
- **Provider Payloads** from internal services (Azure DevOps, GitHub).
- **Azure Resource IDs**, Tenant IDs, and Subscription IDs.
- **Secrets**, tokens, SAS tokens, storage keys, and connection strings.
- **Internal Exceptions** and technical stack traces.

## Getting Started

### Prerequisites
- Node.js 20+
- npm

### Installation
```bash
cd building-blocks/portals/static-status-portal
npm install
```

### Local Development
The portal uses built-in fixtures by default.
```bash
npm run dev
```

### Testing
```bash
npm run test
```

### Build
```bash
npm run build
```

## Infrastructure

The infrastructure is located in `infra/terraform/`. It provisions a basic Azure Static Web App.

### Deployment Proof
```bash
cd infra/terraform
# Use Terraform/OpenTofu to provision:
# terraform init
# terraform validate
```

## References
- [Azure Static Web Apps documentation](https://learn.microsoft.com/en-us/azure/static-web-apps/)
- [Customer-Safe Status Boundary](../../security/customer-safe-status-boundary/README.md)
