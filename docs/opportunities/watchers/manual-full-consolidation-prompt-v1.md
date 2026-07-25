# Manual Full Consolidation Prompt v1

Use this prompt for a deliberate full-catalog consolidation in a dedicated chat.

```text
Execute a full Solution Opportunity Consolidation for GitHub repository `wildersa/azure_ref_kit`. Take repository actions; do not only produce an analysis.

Read and follow the current `main` versions of:
- `AGENTS.md`;
- `docs/opportunities/AGENTS.md`;
- `docs/opportunities/README.md`;
- `docs/opportunities/solution-consolidation-method.md`;
- `docs/opportunities/solution-family-template.md`;
- `docs/opportunities/solution-family-index.yaml`;
- `docs/opportunities/opportunity-family-map.yaml`;
- `docs/opportunities/consolidation-state.yaml`;
- `docs/opportunities/opportunity-index.yaml`;
- `docs/opportunities/opportunity-index.md`;
- every active opportunity document needed for consolidation.

Do not run another discovery round. Do not create new business opportunities. Do not rewrite or weaken `watcher-contract.md`, the simulation-first discovery method, or the preserved discovery watcher.

Goal:

Convert the active opportunity catalog into a small set of reusable solution families while preserving each opportunity as a concrete applied business case.

Use this separation:

business opportunity
→ reusable solution family
→ applied case mapping
→ optional architecture-derivation candidate

The opportunity remains the source of truth for actor, process, problem, Brazilian evidence, regulation, existing solutions, case-specific data, and prototype hypothesis.

The solution family becomes the source of truth for reusable logical architecture, invariant flow, primary intelligent mechanism, deterministic controls, human authority, integration contract, feedback, evaluation, and reusable building blocks.

## Phase 1 — Integrity and inventory

1. Reconcile active documents with both opportunity indexes.
2. Repair deterministic drift, malformed citation tokens, missing active entries, invalid statuses, paths, titles, and counts.
3. Do not change opportunity meaning during repair.
4. Build a normalized fingerprint for every active opportunity containing:
   - actor;
   - bounded process and trigger;
   - primary decision or material outcome;
   - input modalities;
   - primary intelligent mechanism;
   - execution/runtime model;
   - deterministic controls;
   - human authority;
   - integration shape;
   - feedback/evaluation loop;
   - material outcome.

## Phase 2 — Candidate families

Cluster across segments by architectural spine, not by industry or title vocabulary.

A family requires materially compatible:
- trigger and execution model;
- central information transformation;
- primary intelligent mechanism;
- deterministic control boundary;
- human decision boundary;
- data and integration shape;
- feedback and validation model;
- abstention and failure behavior.

Do not create generic buckets such as:
- AI assurance;
- RAG solutions;
- agents;
- multimodal review;
- anomaly detection;
- contradiction detection and ranking.

Name each family by its concrete reusable operational outcome.

Different industries, regulations, systems, schemas, connectors, Azure services, model vendors, and user interfaces are normally adapters or variation points, not separate families.

## Phase 3 — Coherence test

For every candidate family:
- list included opportunities;
- define invariant architecture;
- define allowed variation points;
- identify the closest competing family;
- explain why the family is not too broad;
- explain why included cases do not need separate architectures yet.

Split or leave cases unmapped when one logical architecture cannot represent them without hiding material differences in mechanism, runtime, authority, state, safety, feedback, or evaluation.

A family should normally have at least two credible applied cases. Do not force unique cases into weak families.

## Phase 4 — Create family catalog

Create or update one document per coherent family under `docs/opportunities/solution-families/`, using `solution-family-template.md`.

Each family must define:
- reusable operational outcome;
- suitable and unsuitable processes;
- architecture invariants;
- variation points;
- logical Mermaid architecture;
- deterministic layer;
- one primary intelligent mechanism;
- optional extensions only when applied cases require them;
- human authority and prohibited automated actions;
- canonical data and integration contract;
- feedback, evaluation, abstention, and failure criteria;
- Azure reference mapping without making Azure services the family definition;
- reusable building blocks available and missing;
- applied cases;
- closest-family boundary;
- architecture-derivation status.

## Phase 5 — Map every opportunity

Give every active opportunity exactly one disposition:
- `direct-fit`;
- `fit-with-adapters`;
- `fit-with-extension`;
- `candidate-variant`;
- `unmapped`;
- `duplicate-or-weak`.

Update `opportunity-family-map.yaml`.

Add a concise `## Solution family mapping` section to every active opportunity:
- family ID and name;
- disposition;
- reused architecture;
- case-specific adapters;
- case-specific extension, when material;
- why no separate architecture exists yet.

Update the family document with the same applied-case mapping. Do not duplicate the full family architecture inside opportunity documents.

## Phase 6 — Derivation candidates

Do not create architecture variants in this task.

Only add a case to `derivation_review_queue` when a material structural difference exists, such as:
- the same extension appears in at least two cases;
- authority changes from advisory to governed action;
- runtime topology changes materially;
- training or feedback lifecycle differs structurally;
- tenant, privacy, safety, or regulatory isolation requires another boundary;
- repeated branches make the base architecture unclear;
- prototype and success metrics are no longer comparable.

Do not queue derivation for industry, regulation adapter, Azure SKU, source system, field names, UI, or one optional model alone.

## Phase 7 — Validation

Update and reconcile:
- `solution-family-index.yaml`;
- `opportunity-family-map.yaml`;
- `consolidation-state.yaml`;
- all created family documents;
- all mapped opportunity documents.

Re-fetch every changed file and verify:
- every active opportunity has exactly one mapping;
- bidirectional family/case references agree;
- applied-case counts are correct;
- no active opportunity was silently lost;
- no new opportunity was created;
- no discovery control was modified;
- YAML and Markdown are valid;
- family architecture is smaller and more reusable than copied opportunity architectures.

Commit the documentation changes directly to `main` only after validation.

Final response in Portuguese:

1. Integrity repairs.
2. Families created, with architectural spine and applied cases.
3. Unmapped or duplicate/weak opportunities.
4. Mapping dispositions and material adapters/extensions.
5. Architecture derivation review queue.
6. Files committed and post-write verification.
```
