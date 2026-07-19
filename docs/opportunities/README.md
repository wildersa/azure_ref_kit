# Solution Opportunity Radar

This area tracks real business and operational problems that may justify AI-enabled software, data, automation, integration, machine learning, reinforcement learning, recognition, observability, security, or platform solutions.

The radar is intentionally broader than the current Azure Reference Kit catalog and is not limited to Azure, agents, RAG, or existing building blocks. However, every published opportunity must contain a material intelligent capability. Conventional software and integrations may surround that capability, but cannot be the complete solution alone.

The radar is a solution due-diligence mechanism, not an enthusiastic idea generator. A large, expensive, or frequent problem does not prove that a proposed intelligent solution is feasible, adoptable, or economical.

## Purpose

The radar continuously researches real problems across business segments and records concise solution hypotheses with:

- the segment, company profile, user, and process affected;
- current Brazilian evidence that the problem exists;
- favorable and contrary evidence about the proposed solution pattern;
- a realistic manual, deterministic, or conventional-software baseline;
- a macro solution architecture;
- a required AI, ML, recognition, agent, training, fine-tuning, prediction, or optimization capability;
- data-readiness, integration, operating-cost, and adoption assumptions;
- a bounded pilot with success and kill criteria;
- possible gains and measurable business and model-quality indicators;
- constraints, risks, fallback controls, and human-decision boundaries;
- a symbolic fit score from 0 to 100 with hard feasibility caps;
- relationship to existing repository references, when any.

An opportunity is not automatically an implementation backlog item. It is a researched hypothesis that may later feed `docs/reference-coverage.yaml`, the roadmap, a new building block, a composed solution, or a separate project.

## Files

```text
docs/opportunities/
├─ README.md                    # operating model
├─ watcher-contract.md          # mandatory watcher behavior
├─ radar-config.yaml            # segment rotation, publication rules, and score caps
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
real Brazilian problem
→ problem evidence and affected process
→ strongest non-AI baseline
→ favorable and contrary solution evidence
→ data, cost, adoption and failure analysis
→ solution hypothesis and material intelligent capability
→ bounded pilot, success criteria and kill criteria
→ macro architecture, integrations and controls
→ fit assessment with feasibility caps
→ optional human-approved implementation planning
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
- comparison against the non-AI baseline;
- deterministic validation, human review, abstention, rollback, or manual fallback.

## Problem evidence is not solution evidence

Every opportunity must distinguish:

- **problem evidence:** confirms the pain, cost, delay, risk, or interruption;
- **favorable solution evidence:** confirms that the proposed approach worked under comparable conditions;
- **counter-evidence:** failed pilots, cancellations, discontinued deployments, rollbacks, weak accuracy, false-alert burden, poor adoption, unexpected operating cost, or a simpler baseline that worked adequately;
- **inference:** a reasoned implication not directly proven by a source;
- **unknowns:** facts requiring customer data, legal review, experiment, or pilot.

Brazilian loss, shortage, fraud, delay, error, or market-size statistics may prove a problem. They do not prove that vision, prediction, agents, anomaly detection, RAG, or another model will solve it.

## Mandatory counter-evidence research

Research comparable implementations in Portuguese and English. Use segment-appropriate combinations of terms such as:

```text
falhou
cancelado
descontinuado
rollback
piloto
resultados
precisão
falso positivo
adoção
custo operacional
failed
cancelled
discontinued
pilot results
accuracy limitations
false positives
low adoption
operating cost
```

Record contrary evidence even when it reduces the score. When no public comparable deployment or counter-evidence is found, state that explicitly and record the searches. Absence of contrary evidence is not proof of feasibility.

A failure of the same central capability requires a concrete mitigation in scope, architecture, data, capture, operating model, or human workflow. Without mitigation, reject the candidate or keep it as a low-confidence `research-bet` under the caps in `radar-config.yaml`.

## Baseline, data, economics, and pilot

Every candidate must define:

- the current manual process;
- the strongest realistic deterministic, rules-based, analytics, integration, workflow, or conventional-software alternative;
- why intelligence should outperform that alternative;
- the condition under which the non-AI baseline should be preferred;
- data owners, access, volume, labels, coverage, quality, imbalance, privacy, drift, synchronization, and feedback readiness;
- principal capture, hardware, integration, inference, storage, model-operations, support, and human-review cost drivers;
- a narrow pilot population or process slice;
- baseline or control group;
- business, model-quality, adoption, safety, and compliance success criteria;
- explicit kill criteria that end or redesign the pilot.

Do not invent ROI. Define hypotheses, cost drivers, measurement methods, and decision thresholds.

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
4. Research current Brazilian problems and solution patterns.
5. Search comparable successes and failures.
6. Compare against the strongest non-AI baseline.
7. Assess data readiness, economics, pilot boundaries, and kill criteria.
8. Check semantic duplication against all existing opportunities.
9. Publish at most one opportunity when evidence, intelligent contribution, feasibility, and fit are sufficient.
10. A run may finish with `no-new-fit`; weak ideas, decorative AI, or unmitigated failed solution patterns must not be forced.
11. Append the outcome to `history.jsonl`.
12. Update the segment state and advance the cursor to the next enabled segment.
13. After the final segment, return to the first and explore a different focus.

A segment is never considered permanently finished. The control mechanism ensures coverage without repeatedly researching the same problem.

## Research expectations

Use multiple source types when possible:

1. current Brazilian regulators, public institutions, standards bodies, and official statistics;
2. Brazilian industry associations, sector research, public tenders, operational reports, and credible local cases;
3. current international regulators, standards, and technical research used for comparison;
4. operational guides, incident reports, failed-pilot reports, cancellation reports, and process documentation;
5. academic or technical research;
6. mature open-source projects and public architecture examples;
7. reputable reporting describing concrete operational problems or solution outcomes.

Marketing claims alone are weak evidence. Vendor announcements, demonstrations, prototypes, and unmeasured pilots do not establish production feasibility. Record sources and distinguish direct evidence from inference.

## Opportunity quality gate

Create an opportunity only when it contains:

- a specific actor and process;
- a clear and recurring problem;
- current Brazilian problem evidence;
- separate favorable solution evidence, counter-evidence, inference, and unknowns;
- a declared solution-evidence level and operational maturity;
- a realistic non-AI baseline;
- data-readiness and integration analysis;
- a unit-economics hypothesis without invented ROI;
- a bounded pilot, success criteria, and kill criteria;
- a solution that changes the process, not merely a technology label;
- a material intelligent capability with `ai_dependency: supporting|core`;
- defined model inputs, outputs, evaluation, and safe fallback;
- plausible metrics for measuring business and model value;
- material risks and constraints;
- a macro architecture in Mermaid;
- a fit score with dimension-level reasoning and configured caps;
- duplicate keys and related opportunities.

Reject generic ideas such as `AI chatbot for HR` without defining the user, process, source data, model behavior, boundaries, integrations, evaluation, measurable outcome, baseline, counter-evidence, and pilot rules.

Reject conventional workflow, portal, integration, reporting, or reconciliation solutions when the intelligent capability is absent or merely optional.

Reject or record `no-new-fit` when the manual or deterministic baseline is likely cheaper, safer, and sufficiently effective for the target context.

## Fit score

The symbolic fit score is a decision aid, not a financial forecast.

| Dimension | Range | Meaning |
| --- | ---: | --- |
| Problem evidence and relevance | 0–20 | Strength, recurrence, urgency, and current Brazilian applicability of the problem evidence |
| Business or operational value | 0–20 | Potential value relative to the current and non-AI baseline |
| Technical feasibility | 0–20 | Solution evidence, comparable failures, data availability, integration, model maturity, evaluation, cost, adoption, and operating realism |
| Reuse potential | 0–20 | Applicability across multiple organizations or repeated internal contexts |
| Strategic differentiation | 0–20 | Material advantage created by intelligence beyond deterministic automation |

Record separately:

- `confidence`: low, medium, or high;
- `complexity`: small, medium, large, or research;
- `horizon`: short, medium, or long;
- `solution_evidence_level`: conceptual, prototype, pilot, production, or repeated-production;
- `operational_maturity`: unvalidated, early, or proven;
- `azure_fit`: none, low, medium, or high;
- `ai_dependency`: supporting or core;
- `risk`: low, medium, high, or regulated.

Apply every hard cap in `radar-config.yaml` before publishing. Problem evidence, business value, reuse potential, and differentiation cannot compensate for weak technical feasibility.

High confidence requires credible comparable production evidence, realistic data readiness, and no unresolved failure of the same central capability.

## Gains and metrics

Do not invent percentage improvements. Describe possible gains and propose business and intelligent-capability metrics, including cycle time, effort, error rate, throughput, prediction or recognition quality, false positives, abstention, human overrides, policy reward, cost, adoption, and satisfaction where relevant.

Every pilot must measure incremental value against the selected non-AI baseline. Quantified claims require a cited case study or must be labeled as an experiment target.

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

`Researched` requires evidence about the proposed solution, not only evidence that the problem exists. `Confidence: high` requires comparable production evidence.

Only `approved` opportunities should automatically influence implementation planning. The opportunity watcher may create or update opportunity documents, but must not open an implementation issue unless a separate rule explicitly authorizes it.

## Duplicate prevention

Each opportunity must define:

- `problem_keys` for normalized problem concepts;
- `capability_keys` for major technical and intelligent capabilities;
- `research_queries`, including counter-evidence searches;
- `related_opportunities`;
- a concise uniqueness statement.

Before publishing, compare these fields and the full problem statement against the complete index. Similar models are allowed when they solve materially different processes. A different model attached to the same process is not automatically a new opportunity.

## Relationship to Azure Reference Kit

For each opportunity, classify repository alignment:

- `reuse-existing`: the current kit already contains most required capabilities;
- `extend-kit`: the opportunity reveals useful missing building blocks or references;
- `new-solution`: it can compose existing and new blocks into a reference solution;
- `outside-current-kit`: valuable but better treated as an independent product, experiment, or architecture study.

The repository relationship is descriptive. It must not increase the opportunity score merely because the kit already contains relevant services or building blocks.