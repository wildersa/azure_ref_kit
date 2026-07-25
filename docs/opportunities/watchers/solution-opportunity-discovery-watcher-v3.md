# Solution Opportunity Discovery Watcher v3

## Status

Current discovery watcher prompt with independent segment and technical-focus cursors.

This version preserves the workflow-simulation-first method from v2. The technical focus changes which compatible processes the round deliberately inspects; it never predetermines an algorithm or forces publication.

## Prompt

```text
Execute one Solution Opportunity Radar round for GitHub repository `wildersa/azure_ref_kit`. Take repository actions; do not only report.

Read and follow the current `main` versions of:
- `AGENTS.md`
- `docs/opportunities/AGENTS.md`
- `docs/opportunities/watcher-contract.md`
- `docs/opportunities/README.md`
- `docs/opportunities/technical-focus-rotation.md`
- `docs/opportunities/radar-config.yaml`
- `docs/opportunities/radar-state.yaml`
- `docs/opportunities/opportunity-index.yaml`
- `docs/opportunities/opportunity-index.md`
- `docs/opportunities/opportunity-template.md`
- `docs/opportunities/opportunity-technical-classification-template.md`
- recent relevant entries from `docs/opportunities/history.jsonl`

Create at most one differentiated Solution Opportunity Brief, or record `no-new-fit` for a valid repository-defined reason.

## 1. Repository integrity first

Before discovery, reconcile the radar artifacts:
- every document with active status (`hypothesis`, `researched`, `shortlisted`, `approved`, `implementing`, or `implemented`) must appear exactly once in both active indexes;
- rejected, superseded, and parked records must not appear in active indexes;
- dashboard counts, YAML entries, Markdown rows, segment state, last result, and document status must agree;
- the segment cursor and technical-focus cursor must each identify exactly one valid enabled entry;
- remove or repair malformed generated artifacts such as internal ChatGPT citation tokens (`cite`, `turn...search...`) in repository Markdown;
- repair deterministic drift in the same run before publishing a new candidate.

After repository writes, re-fetch every changed document, both indexes, radar state, and configuration when changed. Do not finish until the published ID, counts, tags, history event, and both cursors are consistent.

## 2. Select both discovery axes

Read the current independent cursors from `radar-state.yaml`:

```text
current segment
+
current technical focus
```

The segment provides the operating context. The technical focus tells the watcher which process characteristics to inspect deliberately.

The technical focus is not a mandatory solution. Do not begin with an algorithm and invent a matching problem.

Use this order:

```text
segment + technical focus
→ choose compatible operating archetypes and bounded activities
→ simulate real work independently of a solution
→ inspect decisions, data, labels, outcomes, rewards, sequences, candidate sets, or tool-use needs relevant to the focus
→ test deterministic, statistical, simpler-model, existing-product, and process alternatives
→ accept, narrow, redesign, or reject the technical hypothesis
```

A round may finish with `no-new-fit` when the selected focus does not expose a credible compatible process, data path, training path, or measurable intervention.

## 3. Simulate work before researching ideas

Choose one or more concrete organization archetypes and actors in the current segment whose real work can plausibly expose the selected technical focus.

Define organization and size, actor and authority, trigger, objective, completion condition, inputs, systems, physical context, constraints, and handoffs.

Cover at least:
1. normal flow;
2. exception flow with incomplete, contradictory, ambiguous, unusual, or high-risk inputs;
3. peak or degraded flow with volume, staffing, system, equipment, deadline, or disruption pressure.

Trace information, actions, decisions, uncertainty, queues, handoffs, re-entry, duplication, reconciliation, errors, consequences, and feedback signals. Mark assumptions and synthetic events explicitly.

Use the current technical focus to decide what additional signals to inspect. Examples:
- supervised ML: observation unit, prediction-time features, later outcome, label source, imbalance, leakage;
- anomaly learning: operating envelope, peer groups, rare deviations, review corrections, absent labels;
- sequence models: temporal order, windows, state changes, delayed outcomes, degradation, seasonality;
- specialized neural networks: image, video, audio, waveform, graph, spatial, or multimodal structure;
- small NLP models: bounded classification, extraction, routing, matching, latency, privacy, and cost constraints;
- RAG: knowledge source, retrieval need, source authority, update cadence, grounded evaluation;
- agents: multi-step goal, tools, permissions, changing state, checkpoints, planning and action boundaries;
- ranking: candidate set, eligibility, ordering decision, observed choice or outcome;
- causal/uplift: intervention alternatives, treatment assignment, confounding, outcome, policy question;
- bandits/RL: repeated state, actions, reward, delayed effect, exploration constraints, safe offline or simulated evaluation;
- forecasting/optimization: future demand or capacity plus constraints, objective function, feasible actions, solver baseline.

Generate several candidate interventions from the simulations. Test process redesign, identifiers, forms, structured data, integration, rules, search, analytics, dashboards, alerts, queues, ordinary automation, statistical methods, and simpler ML first.

Keep AI only where a material recognition, prediction, ranking, recommendation, optimization, generation, retrieval, multimodal, causal, sequence, or governed tool-use gap remains.

Do not force the selected focus. When another mechanism fits better, either reject the focus for this round or record `no-new-fit`; do not silently publish an unrelated familiar LLM/RAG opportunity.

## 4. Portfolio-coherence and coverage gate

Before selecting a candidate, compare it with:
- all active opportunities in the same segment;
- the eight most recently published active opportunities;
- repository-wide actor, process, decision, capability, data-modality, model-strategy, and outcome keys;
- recent technical-focus history and configured coverage targets.

A candidate must be materially different in actor, bounded process, decision or exception, data modality, intelligent mechanism, integration boundary, and measurable outcome.

Do not publish merely another variant of:
- read-only evidence assurance;
- cross-document reconciliation;
- contradiction detection;
- risk-ranked human review;
- generic anomaly detection, RAG, agent, dashboard, or orchestration.

Those patterns are allowed only when the exact operational mechanism and outcome are genuinely distinct and the brief explains why existing repository cases and solution families do not already represent the same opportunity.

Do not default titles to `assurance`. Name the concrete operational outcome.

Coverage targets are investigation targets, not publication quotas:
- seriously investigate custom training or fine-tuning in at least the configured minimum share of rounds;
- avoid defaulting beyond the configured maximum share to pretrained LLM or RAG as the primary investigated mechanism;
- investigate at least one credible RL, bandit, causal, or uplift process per technical-focus cycle.

Never manufacture an opportunity to satisfy a target. `no-new-fit` is valid after adequate simulation and comparison.

## 5. Research after candidate generation

Research the web in Portuguese and English only after initial simulation and candidate generation.

Use research to validate current Brazilian relevance, regulation, operating guidance, assumptions, technical plausibility, data and label plausibility, failures, false positives, adoption issues, cost constraints, simpler alternatives, and current official, commercial, sector, roadmap, API, tender, and open-source solutions.

Every active opportunity requires at least one load-bearing Brazilian source published or materially updated within the previous 18 months. Regulated opportunities require current Brazilian official context. Foreign evidence may support plausibility or limitations but must not define Brazilian law or market assumptions.

Choose exactly one disposition: `build`, `extend`, `integrate`, `adopt`, or `no-new-fit`.

## 6. Technical classification and data analysis

Every newly published or materially revalidated opportunity must include the complete block from `opportunity-technical-classification-template.md`:

```yaml
technical_focus:
technical_class:
model_strategy:
candidate_model_families:
learning_paradigm:
data_modalities:
interaction_pattern:
training_requirement:
data_readiness:
```

Candidate model families are hypotheses, not commitments. Compare them with deterministic, statistical, simpler ML, pretrained, existing-product, and current-process baselines.

The full `training_data` analysis is mandatory when:
- `model_strategy` contains `custom-trained` or `fine-tuned`;
- `training_requirement` is `required`;
- the primary mechanism uses learned prediction, sequence modeling, specialized neural networks, recommendation, causal or uplift learning, contextual bandits, reinforcement learning, or learned forecasting.

Use exactly:

```yaml
training_data:
  observation_unit:
  input_data:
  target_or_reward:
  label_source:
  prediction_time:
  expected_volume:
  class_balance:
  historical_coverage:
  train_validation_split:
  leakage_risks:
  representativeness_risks:
  feedback_loop:
  privacy_and_usage_constraints:
  fallback_if_data_is_insufficient:
```

Separate confirmed facts, simulation assumptions, and unknowns. Do not invent dataset size, label availability, balance, coverage, or data quality.

For trainable approaches, classify readiness as exactly one of:
- `ready`;
- `viable-with-data-work`;
- `pilot-data-needed`;
- `not-currently-trainable`.

Fine-tuning must be justified against prompting, RAG, pretrained inference, compact supervised models, and conventional training. Do not use fine-tuning as a decorative strategy.

## 7. AI minimalism and dependency

Define one primary intelligent mechanism for the prototype. Use at most one optional secondary model component unless the brief proves why more are indispensable.

Do not create a kitchen-sink architecture containing document models, LLMs, embeddings, cross-encoders, graph ML, vision models, anomaly models, and rankers merely because they are plausible.

Set `ai_dependency: core` only when the opportunity's material value collapses without the model-based capability. Use `supporting` when deterministic workflow or integration delivers the primary value and AI improves exceptions or efficiency.

Distinguish agent, LLM, recognition, prediction, sequence modeling, ranking, causal estimation, optimization, rules, APIs, databases, queues, orchestration, and human approval. State `Agent: not used` and `LLM: not used` when applicable.

## 8. Brief quality

Use `opportunity-template.md` plus `opportunity-technical-classification-template.md`. Avoid repeating the same claim across sections. Keep architecture and prototype proportional to the bounded experiment.

Every brief must include operational simulation, deterministic and existing-product baselines, exact uncovered gap, current Brazilian evidence, existing-solution comparison, `Where AI enters`, technical classification, data and feedback assumptions, conditional training-data analysis, bounded prototype, incremental-value metrics, failure/redesign criteria, controls, uncertainty, duplicate keys, and uniqueness statement.

Never embed internal citation markers or conversation references in repository files. Use normal Markdown links in the Sources section.

Existing active opportunities are not bulk-tagged by guesswork. Add the technical classification when an existing case is materially revalidated or updated after reading its complete document.

## 9. Publication and independent cursor advancement

When publishing or recording `no-new-fit`:
- create or update the complete opportunity document when applicable;
- update both active indexes when applicable;
- append history with both `segment` and `technical_focus`;
- record technical-focus result as `fit`, `rejected`, `no-compatible-process`, or `insufficient-data-path`;
- for published opportunities also record `model_strategy`, `training_requirement`, and `data_readiness`;
- update segment state and operational `next_focus`;
- update technical-focus coverage state;
- advance the segment cursor exactly once;
- advance the technical-focus cursor exactly once;
- commit directly to `main`.

Do not reset one cursor when the other completes a cycle. Each cursor maintains its own completed-cycle count.

Do not open implementation issues, add runtime code, modify solution-family consolidation artifacts, or approve implementation without explicit human direction.

Final summary in Portuguese, concise:

Integrity:
- drift found/repaired: ...
- active index count: ...

Round axes:
- segment: ...
- technical focus: ...
- process signals sought: ...

Operational simulation:
- organization and actor: ...
- process and scenarios: ...
- deterministic/statistical baseline: ...
- remaining opportunity: ...

Technical hypothesis:
- fit result: fit | rejected | no-compatible-process | insufficient-data-path
- technical class: ...
- candidate model families: ...
- model strategy: ...
- training requirement: ...
- data readiness: ...
- primary training-data risk: ... | not applicable

Portfolio coherence:
- closest repository patterns: ...
- material differentiation: ...
- repeated-pattern gate: passed | rejected
- coverage target effect: ...

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
- opportunity published/revalidated/rejected/no-new-fit: ...
- files committed: ...
- segment cursor: old → new
- technical-focus cursor: old → new
- verification after write: passed | failed
```

## Separation rule

This watcher owns opportunity discovery, technical-lens coverage, and portfolio novelty. It does not own solution-family consolidation or architecture derivation.
