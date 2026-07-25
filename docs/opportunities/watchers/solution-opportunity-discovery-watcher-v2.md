# Solution Opportunity Discovery Watcher v2

## Status

Preserved discovery watcher prompt as of 2026-07-25.

This method remains valid and independent from solution consolidation. It discovers or rejects concrete opportunities by simulating work first. Consolidation must not rewrite or weaken it.

## Prompt

```text
Execute one Solution Opportunity Radar round for GitHub repository `wildersa/azure_ref_kit`. Take repository actions; do not only report.

Read and follow the current `main` versions of:
- `AGENTS.md`
- `docs/opportunities/watcher-contract.md`
- `docs/opportunities/README.md`
- `docs/opportunities/radar-config.yaml`
- `docs/opportunities/radar-state.yaml`
- `docs/opportunities/opportunity-index.yaml`
- `docs/opportunities/opportunity-index.md`
- `docs/opportunities/opportunity-template.md`
- recent relevant entries from `docs/opportunities/history.jsonl`

Create at most one differentiated Solution Opportunity Brief, or record `no-new-fit` for a valid repository-defined reason.

## 1. Repository integrity first

Before discovery, reconcile the radar artifacts:
- every document with active status (`hypothesis`, `researched`, `shortlisted`, `approved`, `implementing`, or `implemented`) must appear exactly once in both active indexes;
- rejected, superseded, and parked records must not appear in active indexes;
- dashboard counts, YAML entries, Markdown rows, segment state, last result, and document status must agree;
- remove or repair malformed generated artifacts such as internal ChatGPT citation tokens (`cite`, `turn...search...`) in repository Markdown;
- repair deterministic drift in the same run before publishing a new candidate.

After repository writes, re-fetch the changed document, both indexes, and radar state. Do not finish until the published ID and counts are consistent.

## 2. Simulate work before researching ideas

Choose a concrete organization archetype and actor in the current round-robin segment. Simulate a bounded activity independently of any proposed technology.

Define the organization and size, actor and authority, trigger, objective, completion condition, inputs, systems, physical context, constraints, and handoffs.

Cover at least:
1. normal flow;
2. exception flow with incomplete, contradictory, ambiguous, unusual, or high-risk inputs;
3. peak or degraded flow with volume, staffing, system, equipment, deadline, or disruption pressure.

Trace information, actions, decisions, uncertainty, queues, handoffs, re-entry, duplication, reconciliation, errors, consequences, and feedback signals. Mark assumptions and synthetic events explicitly.

Generate several candidate interventions from the simulations. Test process redesign, identifiers, forms, structured data, integration, rules, search, analytics, dashboards, alerts, queues, and ordinary automation first. Keep AI only where a material recognition, prediction, ranking, recommendation, optimization, generation, retrieval, multimodal, causal, graph, or governed tool-use gap remains.

## 3. Portfolio-coherence gate

Before selecting a candidate, compare it with:
- all active opportunities in the same segment;
- the eight most recently published active opportunities;
- repository-wide capability and problem keys.

A candidate must be materially different in the combination of actor, bounded process, decision or exception, data modality, intelligent mechanism, integration boundary, and measurable outcome.

Do not publish merely another variant of:
- read-only evidence assurance;
- cross-document reconciliation;
- contradiction detection;
- risk-ranked human review;
- generic anomaly detection, RAG, agent, dashboard, or orchestration.

Those patterns are allowed only when the exact operational mechanism and outcome are genuinely distinct and the brief explains why existing repository building blocks do not already represent the same opportunity.

Do not default titles to `assurance`. Name the concrete operational outcome. Use `no-new-fit` when the remaining candidates are only thematic variants of existing opportunities.

## 4. Research after candidate generation

Research the web in Portuguese and English to validate current Brazilian relevance, regulation, operating guidance, assumptions, technical plausibility, failures, false positives, adoption issues, cost constraints, simpler alternatives, and current official/commercial/open-source solutions, APIs, tenders, releases, and roadmaps.

Every active opportunity requires at least one load-bearing Brazilian source published or materially updated within the previous 18 months. Regulated opportunities require current Brazilian official context. Foreign evidence may support plausibility or limitations but must not define Brazilian law or market assumptions.

Choose exactly one disposition: `build`, `extend`, `integrate`, `adopt`, or `no-new-fit`.

## 5. AI minimalism and dependency

Define one primary intelligent mechanism for the prototype. Use at most one optional secondary model component unless the brief proves why more are indispensable.

Do not create a kitchen-sink architecture containing document models, LLMs, embeddings, cross-encoders, graph ML, vision models, anomaly models, and rankers merely because they are plausible.

Set `ai_dependency: core` only when the opportunity's material value collapses without the model-based capability. Use `supporting` when deterministic workflow or integration delivers the primary value and AI improves exceptions or efficiency.

Distinguish agent, LLM, recognition, prediction, ranking, optimization, rules, APIs, databases, queues, orchestration, and human approval. State `Agent: not used` and `LLM: not used` when applicable.

## 6. Brief quality

Use the complete repository template, but avoid repeating the same claim across multiple sections. Keep architecture and prototype proportional to the bounded experiment.

Every brief must include operational simulation, deterministic and existing-product baselines, exact uncovered gap, current Brazilian evidence, existing-solution comparison, `Where AI enters`, data and feedback assumptions, bounded prototype, incremental-value metrics, failure/redesign criteria, controls, uncertainty, duplicate keys, and uniqueness statement.

Never embed internal citation markers or conversation references in repository files. Use normal Markdown links in the Sources section.

## 7. Publication

When publishing, create the complete opportunity document, update both active indexes, append history, update segment state and `next_focus`, advance the cursor, and commit directly to `main`. Rejected records may remain outside active indexes for audit.

Do not open implementation issues, add runtime code, or approve implementation without explicit human direction.

Final summary in Portuguese, concise:

Integrity:
- drift found/repaired: ...
- active index count: ...

Operational simulation:
- organization and actor: ...
- process and scenarios: ...
- deterministic baseline: ...
- remaining opportunity: ...

Portfolio coherence:
- closest repository patterns: ...
- material differentiation: ...
- repeated-pattern gate: passed | rejected

Existing landscape:
- overlap and disposition: ...

Where AI enters:
- primary mechanism: ...
- optional secondary mechanism: ... | none
- ai_dependency: supporting | core
- Agent: ... | not used
- LLM: ... | not used
- human control: ...

Actions:
- opportunity published/rejected/no-new-fit: ...
- files committed: ...
- verification after write: passed | failed
```

## Separation rule

This watcher owns opportunity discovery and portfolio novelty. It does not own solution-family consolidation or architecture derivation.
