# Solution Opportunity Radar

This area tracks real business and operational problems that may justify AI-enabled software, data, automation, integration, machine learning, reinforcement learning, recognition, observability, security, or platform solutions.

The radar is intentionally broader than the current Azure Reference Kit catalog and is not limited to Azure, agents, RAG, or existing building blocks. However, every published opportunity must contain a material intelligent capability. Conventional software and integrations may surround that capability, but cannot be the complete solution alone.

## Purpose

The radar continuously researches real problems across business segments and records concise solution hypotheses with:

- the segment, company profile, user, and process affected;
- evidence that the problem exists;
- a macro solution architecture;
- a required AI, ML, recognition, agent, training, fine-tuning, prediction, or optimization capability;
- likely integrations and supporting technical capabilities;
- possible gains and measurable business and model-quality indicators;
- constraints, risks, fallback controls, and human-decision boundaries;
- a symbolic fit score from 0 to 100;
- relationship to existing repository references, when any.

An opportunity is not automatically an implementation backlog item. It is a researched hypothesis that may later feed `docs/reference-coverage.yaml`, the roadmap, a new building block, a composed solution, or a separate project.

## Files

```text
docs/opportunities/
├─ README.md                    # operating model
├─ watcher-contract.md          # mandatory watcher behavior
├─ radar-config.yaml            # segment rotation and publication rules
├─ radar-state.yaml             # round-robin cursor and per-segment state
├─ opportunity-index.yaml       # structured source of truth
├─ opportunity-index.md         # human-readable dashboard
├─ opportunity-template.md      # document template
├─ history.jsonl                # append-only execution history
└─ segments/
   └─ README.md                 # folder and naming rules
```

Few-shot breadth examples belong only in the automation prompt. They are not repository opportunities, evidence, templates, or preferred solution patterns.

## Core principle

```text
real problem
→ evidence and affected process
→ solution hypothesis
→ material intelligent capability
→ macro architecture and integrations
→ measurable gains, model quality and risks
→ fit assessment
→ optional technical implementation
```

Do not begin with a preferred Azure service, model, or architectural pattern. Start with the problem, then identify an intelligent capability whose removal would materially reduce the solution's value. Surround it with the necessary normal software, deterministic controls, integrations, data, hardware, and human review.

## What counts as an intelligent capability

At least one model-based capability must be `supporting` or `core`, such as:

- training or fine-tuning a machine-learning model;
- generative AI with grounded or evaluated outputs;
- an agent using governed tools and explicit boundaries;
- RAG with retrieval and groundedness evaluation;
- speech, image, video, or document recognition;
- classification, entity extraction, ranking, or recommendation;
- anomaly detection, prediction, or forecasting;
- optimization or reinforcement learning;
- multimodal inference;
- another explicit model-based capability with measurable quality.

`AI dependency: none` and `optional` are invalid. A chat box, summary button, or optional assistant added to a conventional application does not satisfy the requirement.

Every opportunity must state:

- why the intelligent capability is necessary;
- its inputs and outputs;
- training, grounding, fine-tuning, simulation, reward, or inference assumptions;
- model or policy evaluation metrics;
- deterministic validation, human review, abstention, rollback, or manual fallback.

## Diversity and anti-anchoring

The radar must still explore a broad solution space. Across runs, vary:

- model family and intelligent technique;
- business actor and process;
- company size and operational maturity;
- software-centric, hardware-assisted, edge, multimodal, optimization, training, and research-oriented architectures;
- interaction model and delivery channel;
- complexity and time horizon.

Do not repeatedly prefer agents, chat interfaces, RAG, document processing, or existing repository capabilities. Requiring intelligence does not mean requiring generative AI.

The automation prompt may contain compact few-shots solely to demonstrate breadth. The watcher must not use those examples as search queries, evidence, candidate ideas, scoring references, or target distributions.

## Round-robin segment rotation

Each watcher run processes one enabled segment from `radar-config.yaml`.

1. Read `radar-state.yaml` and select `current_segment_index`.
2. Read existing opportunities for that segment.
3. Review its `next_focus`, previous search themes, and recent history.
4. Research current real-world problems and solution patterns.
5. Check semantic duplication against all existing opportunities.
6. Publish at most one new opportunity when evidence, intelligent contribution, and fit are sufficient.
7. A run may finish with `no-new-fit`; weak ideas or decorative AI must not be forced.
8. Append the outcome to `history.jsonl`.
9. Update the segment state and advance the cursor to the next enabled segment.
10. After the final segment, return to the first and explore a different focus.

A segment is never considered permanently finished. The control mechanism ensures coverage without repeatedly researching the same problem.

## Research expectations

Use multiple source types when possible:

1. regulators, public institutions, standards bodies, and official statistics;
2. industry associations and sector research;
3. public case studies from vendors and consultancies;
4. job descriptions, operational guides, public tenders, incident reports, and process documentation;
5. academic or technical research;
6. mature open-source projects and public architecture examples;
7. reputable reporting describing concrete operational problems.

Marketing claims alone are weak evidence. Record sources and distinguish direct evidence from inference.

## Opportunity quality gate

Create an opportunity only when it contains:

- a specific actor and process;
- a clear and recurring problem;
- at least one credible source or multiple weaker corroborating sources;
- a solution that changes the process, not merely a technology label;
- a material intelligent capability with `ai_dependency: supporting|core`;
- defined model inputs, outputs, evaluation, and safe fallback;
- plausible metrics for measuring business and model value;
- material risks and constraints;
- a macro architecture in Mermaid;
- a fit score with dimension-level reasoning;
- duplicate keys and related opportunities.

Reject generic ideas such as `AI chatbot for HR` without defining the user, process, source data, model behavior, boundaries, integrations, evaluation, and measurable outcome.

Reject conventional workflow, portal, integration, reporting, or reconciliation solutions when the intelligent capability is absent or merely optional.

## Fit score

The symbolic fit score is a decision aid, not a financial forecast.

| Dimension | Range | Meaning |
| --- | ---: | --- |
| Problem evidence and relevance | 0–20 | Strength, recurrence, and urgency of the problem evidence |
| Business or operational value | 0–20 | Potential to improve cost, time, quality, risk, revenue, or capacity |
| Technical feasibility | 0–20 | Data availability, integration feasibility, model maturity, evaluation, and delivery realism |
| Reuse potential | 0–20 | Applicability across multiple organizations or repeated internal contexts |
| Strategic differentiation | 0–20 | Material advantage created by the intelligent capability beyond simple manual automation |

Record separately:

- `confidence`: low, medium, or high;
- `complexity`: small, medium, large, or research;
- `horizon`: short, medium, or long;
- `azure_fit`: none, low, medium, or high;
- `ai_dependency`: supporting or core;
- `risk`: low, medium, high, or regulated.

A high fit score does not cancel regulatory, privacy, safety, integration, bias, drift, evaluation, or data-availability risk.

## Gains and metrics

Do not invent percentage improvements. Describe possible gains and propose business and intelligent-capability metrics, including cycle time, effort, error rate, throughput, prediction or recognition quality, false positives, abstention, human overrides, policy reward, cost, and satisfaction where relevant.

Quantified claims require a cited case study or must be labeled as an experiment target.

## Status lifecycle

```text
hypothesis
→ researched
→ shortlisted
→ approved
→ implementing
→ implemented
```

Alternative terminal states:

```text
rejected
superseded
parked
```

Only `approved` opportunities should automatically influence implementation planning. The opportunity watcher may create or update opportunity documents, but must not open an implementation issue unless a separate rule explicitly authorizes it.

## Duplicate prevention

Each opportunity must define:

- `problem_keys` for normalized problem concepts;
- `capability_keys` for major technical and intelligent capabilities;
- `research_queries` already used;
- `related_opportunities`;
- a concise uniqueness statement.

Before publishing, compare these fields and the full problem statement against the complete index. Similar models are allowed when they solve materially different processes. A different model attached to the same process is not automatically a new opportunity.

## Relationship to Azure Reference Kit

For each opportunity, classify repository alignment:

- `reuse-existing`: the current kit already contains most required capabilities;
- `extend-kit`: the opportunity reveals useful missing building blocks or references;
- `new-solution`: it can compose existing and new blocks into a reference solution;
- `outside-current-kit`: valuable but better treated as an independent product, experiment, or architecture study.

The repository relationship is descriptive. It must not reduce the opportunity score merely because the kit does not yet support it.
