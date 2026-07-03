# Roadmap

This roadmap defines the prioritized sequence of reference solutions and building blocks for the Azure Reference Kit.

## Phase 1: Foundation & DevOps Visibility (Current)

1. **Foundry + DevOps Agent (Basic)**
   - **Scenario**: A minimal Foundry agent that answers questions about a pipeline/build through a controlled tool boundary.
   - **Key Building Blocks**:
     - `building-blocks/agents/pipeline-assistant-foundry`
     - `building-blocks/functions/devops-status-tool`
   - **Outcome**: A safe, read-only agent that bridge DevOps status to natural language.

2. **Document AI Portal (Standard)**
   - **Scenario**: End-to-end document processing pipeline with a customer-facing status portal.
   - **Key Building Blocks**: OCR, Durable Functions, Static Web Apps.
   - **Status**: Scaffolding exists in `solutions/document-ai-portal/`.

## Phase 2: Agentic Automation & Tooling

3. **Multi-Agent Orchestration with Foundry**
   - **Scenario**: Coordinating multiple specialized agents for complex business processes.

4. **MCP (Model Context Protocol) Tool Integration**
   - **Scenario**: Demonstrating how to use MCP to expose enterprise data to Foundry agents safely.

## Phase 3: Advanced Observability & Governance

5. **AI Cost & Performance Ledger**
   - **Scenario**: Advanced tracking of token usage, latency, and cost per customer/request across multiple services.

---
**Note**: Every future Azure/Foundry/DevOps issue must consult current Microsoft documentation and record material URLs in the PR body.
