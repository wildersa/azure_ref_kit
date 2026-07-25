# Solution Opportunity Consolidation Method

## Goal

Convert the opportunity catalog into a smaller set of reusable solution families without erasing the business-specific cases that revealed them.

The method separates four artifacts:

```text
business opportunity
→ reusable solution family
→ applied case mapping
→ optional derived architecture
```

- **Opportunity:** a concrete actor, process, problem, evidence, and prototype hypothesis.
- **Solution family:** a reusable logical solution pattern that can serve multiple opportunities.
- **Applied case:** how one opportunity uses a solution family, including required adapters and deviations.
- **Derived architecture:** a separate architecture variant created only when repeated applied cases prove that the base family cannot represent a material structural difference cleanly.

Consolidation must not rewrite every opportunity into the same generic architecture. It must preserve the operational reason each case exists.

## Repository model

Use these artifacts:

```text
docs/opportunities/
├─ solution-consolidation-method.md
├─ solution-family-index.yaml
├─ opportunity-family-map.yaml
├─ consolidation-state.yaml
├─ solution-family-template.md
├─ solution-families/
│  └─ <FAMILY-ID>-<slug>.md
└─ segments/
   └─ <segment>/<opportunity>.md
```

The opportunity documents remain the source of truth for business context, evidence, actors, process, regulation, and prototype assumptions.

The solution-family documents become the source of truth for reusable logical architecture, invariant capabilities, variation points, controls, and reusable building blocks.

## Consolidation unit

A family is not created because several opportunities use the words `assurance`, `ranking`, `RAG`, or `agent`.

Group opportunities only when they share a material architectural spine:

- same type of trigger and execution model;
- same central information transformation;
- same primary intelligent mechanism;
- same deterministic control boundary;
- same human decision boundary;
- same major data stores and integration shape;
- same validation and feedback loop;
- same failure and abstention model.

Business domain, terminology, regulation, adapters, models, or user interface may vary without requiring a new family.

## Required fingerprints

Before clustering, describe every opportunity with this fingerprint:

```yaml
opportunity_id: ENERGY-003
actor: field-work safety coordinator
process: authorize a field-work package
trigger: maintenance work package ready for release
primary_decision: hold, correct, or release for human authorization
input_modalities: [documents, topology, structured records, images]
primary_intelligent_mechanism: cross-source entity and state reconciliation
execution_mode: asynchronous-review
human_authority: authorized safety supervisor
hard_deterministic_controls: [identity, qualification, version, mandatory tests]
integration_shape: read-only assurance layer
feedback: reviewer-confirmed contradiction types
material_outcome: prevent mismatched work evidence from reaching authorization
```

The fingerprint must describe what the solution does, not only the business subject.

## Consolidation workflow

### 1. Inventory and normalize

- Reconcile active opportunity indexes and document statuses.
- Extract fingerprints for every active opportunity.
- Normalize synonymous capability and architecture terms.
- Identify malformed, incomplete, rejected, superseded, or parked records.
- Do not change opportunity meaning during normalization.

### 2. Generate candidate families

Cluster by architectural spine, not by segment.

For every proposed family, list:

- included opportunities;
- invariant process and architecture;
- allowed variation points;
- closest competing family;
- why the family is not merely a broad category;
- why included cases do not need separate architectures yet.

A family should normally have at least two credible applied cases. A uniquely strong opportunity may remain `unmapped` until another case appears.

### 3. Test family coherence

A family is coherent only when one logical architecture can represent all included cases without hiding material differences.

Test these dimensions:

| Dimension | Same family when | Separate or candidate variant when |
| --- | --- | --- |
| Primary mechanism | same model-based job | fundamentally different inference or optimization loop |
| Runtime | configurable deployment mode | synchronous versus durable/edge topology changes the control model |
| Authority | same human/deterministic decision boundary | system is allowed to act where the base family is advisory only |
| Data | adapters and schemas differ | different data lifecycle, feedback, privacy, or state model |
| Integration | different connectors | orchestration or write-back semantics change materially |
| Safety | domain controls plug into the same gate | safety case requires a different isolation boundary |
| Evaluation | same metric family | success requires a different causal or operational experiment |

Do not create separate families only because Azure services, vendors, model names, or UI channels differ.

### 4. Define the reusable family

Each solution family must declare:

- concrete reusable outcome;
- suitable and unsuitable processes;
- invariant logical flow;
- deterministic layer;
- primary intelligent mechanism;
- optional extension points;
- human authority and prohibited actions;
- required data contracts;
- feedback and evaluation contract;
- privacy, security, safety, and audit boundaries;
- Azure reference mapping without making Azure services the definition;
- reusable building blocks already available or missing;
- applied cases and their adjustments.

Keep one primary intelligent mechanism. Add secondary components only when required by an applied case and label them as optional extensions.

### 5. Map every opportunity

Each active opportunity receives exactly one mapping disposition:

- `direct-fit`: uses the family without structural change;
- `fit-with-adapters`: domain connectors, schemas, rules, terminology, or UI differ;
- `fit-with-extension`: requires an optional capability not present in the base family;
- `candidate-variant`: material architecture difference may justify derivation later;
- `unmapped`: no coherent family yet;
- `duplicate-or-weak`: should be reviewed for consolidation, parking, rejection, or supersession.

Record mappings in `opportunity-family-map.yaml` and add a concise `Solution family mapping` section to the opportunity document.

The opportunity section must state:

```md
## Solution family mapping

- **Family:** `<FAMILY-ID> — <name>`
- **Disposition:** direct-fit | fit-with-adapters | fit-with-extension | candidate-variant | unmapped
- **Reused architecture:** <invariant flow and capabilities reused>
- **Case-specific adapters:** <systems, schemas, rules, regulations, channels>
- **Case-specific extension:** <only when material>
- **Why no separate architecture yet:** <reason>
```

Do not copy the complete family architecture into each opportunity.

### 6. Register applied cases in both directions

The family document lists each applied opportunity with:

- actor and bounded process;
- mapping disposition;
- adapters;
- extensions;
- validation delta;
- architecture-derivation signal.

The opportunity links back to the family. Both references must agree.

### 7. Review architecture derivation separately

Consolidation does not automatically create architecture variants.

A later derivation review may create a new family or variant only when one or more are true:

- the same extension appears in at least two applied cases;
- authority changes from advisory to governed action or optimization;
- runtime topology changes materially, such as batch to edge real-time or durable agent execution;
- feedback/training lifecycle is structurally different;
- privacy, tenant, safety, or regulatory isolation requires a separate boundary;
- the base diagram needs repeated conditional branches that obscure the normal flow;
- prototype and success metrics are no longer comparable with the base family.

Do not derive for:

- a different industry;
- a different Azure SKU;
- a different source system;
- different field names or regulation adapters;
- a single optional model;
- different UI wording;
- hypothetical future reuse.

## Consolidation quality gates

A completed round must satisfy:

- no active opportunity is silently lost;
- every mapping is evidence-based and reversible;
- no family is a generic bucket such as `AI assurance`, `RAG`, or `agents`;
- every family has a named operational outcome and architectural spine;
- family invariants and variation points are explicit;
- domain-specific regulation remains in the applied opportunity;
- the family architecture remains smaller than the combined opportunity architectures;
- duplicate architecture text is reduced rather than relocated;
- `core` versus `supporting` AI dependency is reconsidered per applied case;
- index, map, state, family documents, and opportunity references agree.

## Consolidation round size

A watcher round should process one coherent candidate family or 3–6 closely related opportunities.

Do not attempt to rewrite the entire catalog in one scheduled run.

A full manual consolidation may process the entire catalog, but it must still produce and validate families incrementally.

## State model

Use `consolidation-state.yaml` to track:

```yaml
schema_version: 1
phase: inventory | clustering | mapping | derivation-review | complete
last_run: null
next_candidate_group: null
processed_opportunities: []
unmapped_opportunities: []
family_review_queue: []
derivation_review_queue: []
```

## Final result

The target repository state is:

```text
many concrete opportunities
→ few reusable solution families
→ explicit applied-case adjustments
→ rare, evidence-based architecture variants
```

The discovery method remains independent. Discovery produces or revises opportunities. Consolidation organizes them. Architecture derivation remains a separate decision.