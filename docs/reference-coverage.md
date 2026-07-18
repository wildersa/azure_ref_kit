# Azure AI Reference Coverage

This dashboard is generated from `docs/reference-coverage.yaml`. Edit the YAML source, then regenerate this file.

**Last reviewed:** 2026-07-18

## Coverage summary

| Covered | Partial | None | Total domains |
| ---: | ---: | ---: | ---: |
| 0 | 10 | 8 | 18 |

## Continuous discovery workflow

1. Read docs/catalog.json and this coverage map before proposing new work.
2. Select a domain with coverage none or partial, prioritizing clear reusable gaps.
3. Research current official sources first, then inspect mature external examples when useful.
4. Record one to three bounded candidates with sources, rationale, priority, and status.
5. Open only one immediately executable implementation issue unless independent capacity is explicit.
6. Update the candidate status and issue number when work starts, then record the implemented path after merge.

### Source priority

- Microsoft Learn and product documentation
- Azure Architecture Center
- Azure Samples and official Microsoft GitHub repositories
- Mature external repositories and public reference solutions

### Selection rules

- Cover the full Azure AI ecosystem, not only agents.
- Prefer a reusable building block or a small composed solution with observable value.
- Adapt external ideas to repository contracts; do not copy implementations without reviewing license, security, and Azure fit.
- Do not repeat a rejected candidate unless its status is changed to revisit with a new reason.
- Prefer missing capabilities over another variant of an already well-covered example.

## Domain overview

| Domain | Coverage | Implemented references | Open gaps | Candidates | Last reviewed |
| --- | --- | ---: | ---: | ---: | --- |
| Azure OpenAI | `none` | 0 | 3 | 0 | 2026-07-18 |
| Microsoft Foundry and agents | `partial` | 1 | 2 | 0 | 2026-07-18 |
| Azure AI Document Intelligence | `partial` | 2 | 3 | 0 | 2026-07-18 |
| Azure AI Search and RAG | `none` | 0 | 3 | 0 | 2026-07-18 |
| Azure AI Speech | `none` | 0 | 3 | 0 | 2026-07-18 |
| Azure AI Vision | `none` | 0 | 3 | 0 | 2026-07-18 |
| Azure AI Language | `none` | 0 | 2 | 0 | 2026-07-18 |
| Azure AI Content Safety | `none` | 0 | 3 | 0 | 2026-07-18 |
| Azure Machine Learning | `none` | 0 | 3 | 0 | 2026-07-18 |
| Prompt flow, evaluation, and quality | `none` | 0 | 3 | 0 | 2026-07-18 |
| AI observability | `partial` | 1 | 2 | 0 | 2026-07-18 |
| AI Gateway and API Management | `partial` | 1 | 2 | 0 | 2026-07-18 |
| Functions, Durable Functions, and event-driven AI | `partial` | 2 | 2 | 0 | 2026-07-18 |
| Storage and AI data foundations | `partial` | 1 | 2 | 0 | 2026-07-18 |
| Security, identity, and network boundaries | `partial` | 1 | 2 | 0 | 2026-07-18 |
| DevOps, IaC, and deployment | `partial` | 2 | 2 | 0 | 2026-07-18 |
| Portals and APIs for AI solutions | `partial` | 2 | 2 | 0 | 2026-07-18 |
| Composed Azure AI solutions | `partial` | 1 | 5 | 0 | 2026-07-18 |

## Domain details

### Azure OpenAI

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Minimal model inference reference independent from an agent runtime`
- `Structured output and safe retry reference`
- `Model deployment, quota, and cost guidance tied to a working example`

**Candidates**

- No candidate recorded.

### Microsoft Foundry and agents

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/agents/pipeline-assistant-foundry`

**Known gaps**

- `Minimal Foundry agent lifecycle reference`
- `Tool, evaluation, and publishing variants with current SDK guidance`

**Candidates**

- No candidate recorded.

### Azure AI Document Intelligence

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/functions/ocr-document-intelligence`
- `solutions/document-ai-portal`

**Known gaps**

- `Document classification pipeline`
- `Custom extraction reference`
- `Human validation workflow`

**Candidates**

- No candidate recorded.

### Azure AI Search and RAG

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Indexing and retrieval building block`
- `Grounded RAG solution with evaluation`
- `Hybrid and vector search comparison`

**Candidates**

- No candidate recorded.

### Azure AI Speech

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Speech-to-text reference`
- `Text-to-speech reference`
- `Batch transcription workflow`

**Candidates**

- No candidate recorded.

### Azure AI Vision

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Image analysis reference`
- `OCR versus Document Intelligence decision example`
- `Vision-enabled composed solution`

**Candidates**

- No candidate recorded.

### Azure AI Language

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Classification and entity extraction reference`
- `Summarization or conversation analysis reference`

**Candidates**

- No candidate recorded.

### Azure AI Content Safety

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Text moderation building block`
- `Image moderation building block`
- `Safe integration pattern for AI applications`

**Candidates**

- No candidate recorded.

### Azure Machine Learning

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Training and registration reference`
- `Batch endpoint reference`
- `Managed online endpoint reference`

**Candidates**

- No candidate recorded.

### Prompt flow, evaluation, and quality

Coverage: `none`  
Last reviewed: `2026-07-18`

**Implemented references**

- No implemented reference recorded.

**Known gaps**

- `Dataset-driven evaluation example`
- `Quality and safety scorecard`
- `CI validation for prompts or AI flows`

**Candidates**

- No candidate recorded.

### AI observability

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/observability`

**Known gaps**

- `End-to-end tracing example for a non-agent AI workload`
- `Cost and token telemetry reference`

**Candidates**

- No candidate recorded.

### AI Gateway and API Management

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/gateways/apim-ai-gateway`

**Known gaps**

- `Gateway-backed non-agent model application`
- `Multi-backend routing and fallback reference`

**Candidates**

- No candidate recorded.

### Functions, Durable Functions, and event-driven AI

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/functions`
- `building-blocks/pipelines/durable-basic-pipeline`

**Known gaps**

- `Event Grid or Service Bus AI processing reference`
- `Long-running non-agent AI workflow`

**Candidates**

- No candidate recorded.

### Storage and AI data foundations

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/storage/blob-artifact-store`

**Known gaps**

- `Dataset and lineage reference`
- `Secure ingestion pattern for AI workloads`

**Candidates**

- No candidate recorded.

### Security, identity, and network boundaries

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/security`

**Known gaps**

- `End-to-end managed identity reference across an AI solution`
- `Private networking example tied to a concrete solution`

**Candidates**

- No candidate recorded.

### DevOps, IaC, and deployment

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/devops/github-actions-azure-deploy`
- `building-blocks/devops/azure-pipelines-azure-deploy`

**Known gaps**

- `Deployment reference for each major AI workload family`
- `Reusable environment promotion and validation pattern`

**Candidates**

- No candidate recorded.

### Portals and APIs for AI solutions

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `building-blocks/portals/static-status-portal`
- `building-blocks/functions/portal-api-functions`

**Known gaps**

- `Generic AI result portal independent from Document AI`
- `Streaming API reference`

**Candidates**

- No candidate recorded.

### Composed Azure AI solutions

Coverage: `partial`  
Last reviewed: `2026-07-18`

**Implemented references**

- `solutions/document-ai-portal`

**Known gaps**

- `Search and RAG solution`
- `Speech solution`
- `Vision solution`
- `Machine learning solution`
- `Content safety integration solution`

**Candidates**

- No candidate recorded.

## Commands

```bash
python scripts/generate_reference_coverage.py
python scripts/generate_reference_coverage.py --check
```
