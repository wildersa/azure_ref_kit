# Solution Consolidation Watcher v1

## Purpose

Run incremental consolidation rounds over active solution opportunities without changing the discovery method.

This watcher organizes existing opportunities into reusable solution families. It does not discover new business opportunities and does not create implementation architecture variants automatically.

## Prompt

```text
Execute one Solution Consolidation round for GitHub repository `wildersa/azure_ref_kit`. Take repository actions; do not only report.

Read and follow the current `main` versions of:
- `AGENTS.md`
- `docs/opportunities/AGENTS.md`
- `docs/opportunities/README.md`
- `docs/opportunities/solution-consolidation-method.md`
- `docs/opportunities/solution-family-template.md`
- `docs/opportunities/solution-family-index.yaml`
- `docs/opportunities/opportunity-family-map.yaml`
- `docs/opportunities/consolidation-state.yaml`
- `docs/opportunities/opportunity-index.yaml`
- `docs/opportunities/opportunity-index.md`
- the active opportunity documents required for the current candidate group

Do not run the discovery radar. Do not research or publish a new opportunity. Do not rewrite `watcher-contract.md`, the operational-simulation method, or the discovery watcher prompt.

## 1. Integrity before consolidation

Reconcile active opportunity documents with both active indexes before clustering:
- active statuses must appear exactly once in both indexes;
- rejected, parked, and superseded records must not appear in active indexes;
- IDs, status, document paths, titles, and counts must agree;
- malformed internal citation markers or generated artifacts must be repaired;
- record deterministic repairs before continuing.

Do not change the business meaning of an opportunity during integrity repair.

## 2. Select one bounded consolidation group

Use `consolidation-state.yaml` to select one coherent candidate group of 3–6 opportunities, or one existing family requiring review.

Prefer opportunities that appear to share an architectural spine. Do not group only by segment, title vocabulary, `assurance`, `ranking`, `RAG`, `agent`, or a generic AI capability.

Create a normalized fingerprint for every selected opportunity:
- actor;
- bounded process and trigger;
- primary decision or operational outcome;
- input modalities;
- primary intelligent mechanism;
- execution/runtime model;
- deterministic controls;
- human authority;
- integration shape;
- feedback/evaluation loop;
- material outcome.

## 3. Test architectural coherence

Compare the selected fingerprints using the consolidation method.

A shared family requires materially compatible:
- trigger and execution model;
- central information transformation;
- primary intelligent mechanism;
- deterministic control boundary;
- human decision boundary;
- data and integration shape;
- feedback and validation model;
- abstention and failure behavior.

Different industries, regulations, source products, schemas, connectors, Azure services, model vendors, and user interfaces are normally adapters or variation points, not separate families.

Do not create a generic family such as `AI assurance`, `RAG`, `agents`, `multimodal review`, or `anomaly detection`.

## 4. Choose one result

Choose exactly one:
- create one proposed solution family;
- extend or correct one existing family;
- map selected opportunities to an existing family;
- mark selected cases `unmapped` because no coherent family exists yet;
- mark a case `duplicate-or-weak` for later portfolio review;
- queue `candidate-variant` for a separate architecture-derivation review.

Do not derive a separate architecture in this watcher.

## 5. Create or update the family

When creating or updating a family, use `solution-family-template.md` and define:
- concrete reusable operational outcome;
- suitable and unsuitable process shapes;
- architecture invariants;
- variation points;
- logical architecture;
- deterministic layer;
- one primary intelligent mechanism;
- optional extensions only when required by an applied case;
- human authority and prohibited actions;
- canonical data and integration contract;
- evaluation, feedback, abstention, and failure criteria;
- Azure reference mapping without making Azure services the family definition;
- available and missing reusable building blocks;
- closest-family boundary;
- architecture-derivation status.

A new family normally requires at least two credible applied cases. A unique case should remain `unmapped` unless its architectural spine is strong enough to justify a proposed family and the reason is explicit.

## 6. Map applied cases bidirectionally

For every processed opportunity choose exactly one disposition:
- `direct-fit`;
- `fit-with-adapters`;
- `fit-with-extension`;
- `candidate-variant`;
- `unmapped`;
- `duplicate-or-weak`.

Update `opportunity-family-map.yaml`.

Add or update a concise `## Solution family mapping` section in each processed opportunity:
- family ID and name;
- disposition;
- reused architecture;
- case-specific adapters;
- case-specific extension, when material;
- why no separate architecture exists yet.

Update the family `Applied cases` table with the same mapping. Do not duplicate the complete family architecture inside opportunity documents.

## 7. Architecture derivation gate

Only queue a derivation review when a material structural difference exists, such as:
- the same extension appears in at least two cases;
- authority changes from advisory to governed action;
- runtime topology changes materially;
- training or feedback lifecycle differs structurally;
- tenant, privacy, safety, or regulatory isolation requires another boundary;
- repeated conditional branches make the base architecture unclear;
- prototype and success metrics are not comparable with the base family.

Do not queue derivation for industry, regulation adapter, Azure SKU, source system, field name, UI, or one optional model alone.

## 8. State and verification

Update:
- `solution-family-index.yaml`;
- `opportunity-family-map.yaml`;
- `consolidation-state.yaml`;
- family document when applicable;
- processed opportunity documents;
- repository history only if the consolidation method defines a dedicated record.

After writes, re-fetch every changed file. Verify:
- every processed opportunity has one mapping;
- both directions agree;
- family applied-case count is correct;
- no opportunity meaning or evidence was lost;
- no new opportunity was created;
- discovery files were not modified;
- YAML and Markdown are valid.

Commit documentation changes directly to `main` only after verification.

Final summary in Portuguese, concise:

Integrity:
- drift found/repaired: ...

Consolidation group:
- opportunities reviewed: ...
- shared architectural spine: ...
- closest competing family: ...

Result:
- family created/updated/mapping only/unmapped/duplicate-or-weak: ...
- mappings: ...
- adapters/extensions: ...
- derivation review queued: yes | no

Verification:
- bidirectional mapping: passed | failed
- discovery method untouched: passed | failed
- files committed: ...
```

## Boundaries

- Preserve `watcher-contract.md` and the discovery watcher as separate controls.
- Do not open implementation issues.
- Do not add runtime code or infrastructure.
- Do not approve a solution family for implementation.
- Do not create architecture variants during consolidation.
