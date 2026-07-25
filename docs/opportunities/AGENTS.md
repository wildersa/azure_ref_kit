# AGENTS.md — Solution Opportunity Radar

These instructions apply to `docs/opportunities/` and override broader repository guidance when executing the Solution Opportunity Radar.

## Discovery order

Use this sequence:

```text
select current segment + independent technical focus
→ simulate compatible actor workflows without proposing a solution
→ expose decisions, exceptions, uncertainty, handoffs, degraded conditions, data, labels, rewards, and feedback
→ test deterministic process, software, statistical, and simpler-model alternatives
→ formulate and accept or reject candidate intelligent interventions
→ research Brazilian relevance, regulation, technical plausibility, data plausibility, and existing solutions
→ publish, extend, integrate, adopt, or record no-new-fit
```

Do not begin with vendor products, market reports, familiar AI patterns, algorithms, or web-search themes and then invent a matching workflow.

The technical focus determines which process characteristics the round deliberately inspects. It does not predetermine the solution. A round may reject the focus or finish with `no-new-fit`.

Follow `technical-focus-rotation.md` for the independent technical cursor, focus taxonomy, coverage targets, technical tags, and conditional training-data analysis.

## Operational simulation

Before broad web research:

- read both independent cursors from `radar-state.yaml`;
- choose concrete organization and actor archetypes in the current segment whose work can plausibly expose the current technical focus;
- bound one operational activity from trigger to outcome;
- simulate normal, exception, and peak or degraded flows;
- trace information, systems, decisions, handoffs, waiting, rework, errors, feedback, labels, rewards, temporal structure, candidate sets, or tool-use requirements relevant to the focus;
- label assumptions and synthetic events explicitly;
- derive multiple candidate opportunity points from the simulation;
- compare with deterministic, statistical, simpler ML, current-product, and current-process baselines.

Before keeping an AI candidate, test whether process redesign, integration, forms, rules, search, analytics, dashboards, alerts, queues, ordinary automation, or a simpler model solves it adequately.

Never force RL, fine-tuning, a neural network, an LLM, RAG, or an agent where the simulated process does not provide the required decision structure, data, labels, reward, knowledge source, tools, or evaluation path.

## Research role

Research follows initial simulation and candidate generation. Use it to:

- validate the load-bearing Brazilian problem;
- confirm current Brazilian regulation or official guidance;
- validate or contradict simulation assumptions;
- verify technical, data, label, training, and integration plausibility and limitations;
- identify existing platforms, products, roadmaps, APIs, tenders, and mature open source;
- prevent duplicate or weakly differentiated opportunities.

Do not require a citation for every simulated micro-step. Do require sources for load-bearing problem claims, regulation, market scale, existing-solution capabilities, roadmaps, and demonstrated outcomes.

## Publication

Follow `watcher-contract.md`, `technical-focus-rotation.md`, `radar-config.yaml`, `opportunity-template.md`, and `opportunity-technical-classification-template.md`.

Every new or materially revalidated active opportunity must include:

- a concrete operational simulation;
- explicit assumptions;
- a material decision, exception, uncertainty, or coordination gap;
- existing-product, deterministic, statistical, and simpler-model baselines when relevant;
- existing-solution landscape and differentiation;
- a material intelligent capability mapped to the process;
- technical classification tags;
- training-data analysis when custom training, fine-tuning, learned forecasting, sequence models, specialized neural networks, recommendation, causal/uplift, bandits, or RL are primary;
- a bounded prototype and measurable failure, redesign, and scale criteria.

Do not invent dataset size, labels, class balance, coverage, or readiness. Separate confirmed facts, simulation assumptions, and unknowns.

Existing opportunities must not be bulk-tagged by guesswork. Add tags when the complete case is materially revalidated or updated.

Failure of external research to suggest an idea is not a valid `no-new-fit` reason.

## State and history

Every completed round must persist and advance both independent cursors exactly once, including `no-new-fit`.

History must record the segment, technical focus, focus result, and, for published opportunities, model strategy, training requirement, and data readiness.

Do not modify solution-family consolidation artifacts during discovery.