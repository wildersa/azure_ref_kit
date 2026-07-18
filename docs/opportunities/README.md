# Solution Opportunity Radar

This area tracks business and operational problems that may justify new software, data, automation, integration, AI, machine learning, reinforcement learning, observability, security, or platform solutions.

The radar is intentionally broader than the current Azure Reference Kit catalog. Existing building blocks may support an opportunity, but they must not limit discovery. The problem and expected outcome come first; technology selection comes later.

## Purpose

The radar continuously researches real problems across business segments and records concise solution hypotheses with:

- the segment, company profile, user, and process affected;
- evidence that the problem exists;
- a macro solution architecture;
- likely integrations and technical capabilities;
- possible gains and measurable indicators;
- constraints, risks, and human-control boundaries;
- a symbolic fit score from 0 to 100;
- relationship to existing repository references, when any.

An opportunity is not automatically an implementation backlog item. It is a researched hypothesis that may later feed `docs/reference-coverage.yaml`, the roadmap, a new building block, a composed solution, or a separate project.

## Files

```text
docs/opportunities/
├─ README.md                    # operating model
├─ radar-config.yaml            # segment rotation and publication rules
├─ radar-state.yaml             # round-robin cursor and per-segment state
├─ opportunity-index.yaml       # structured source of truth
├─ opportunity-index.md         # human-readable dashboard
├─ opportunity-template.md      # document template
├─ history.jsonl                # append-only execution history
└─ segments/
   └─ README.md                 # folder and naming rules
```

## Core principle

```text
real problem
→ evidence and affected process
→ solution hypothesis
→ macro architecture
→ measurable gains and risks
→ fit assessment
→ optional technical implementation
```

Do not begin with a preferred Azure service, AI model, or architectural pattern. Start with the problem and verify whether normal software, integration, analytics, automation, machine learning, generative AI, reinforcement learning, or a combination is justified.

## Breadth anchors, not solution templates

The watcher may use a few short examples only to calibrate the breadth of acceptable opportunities:

- **Small:** an internal HR assistant that answers policy questions from controlled sources and escalates uncertain cases.
- **Field and multimodal:** a Mato Grosso public-sector forensic workflow described by an internal contact, where smart glasses capture audio and video, transcription identifies spoken evidence markers, relevant frames are extracted, and a draft evidence description is prepared for expert validation.
- **Complex and integrated:** document validation combining recognition, rules, system integrations, investigation, human review, and an operational command portal.
- **Optimization:** a log-management platform that builds operational simulations and trains reinforcement-learning policies to recommend safer actions.
- **Non-AI:** a conventional integration and workflow application that removes repeated reconciliation, handoffs, and status checks without using a model.

These examples are not preferred sectors, required architectures, public evidence, or ideas to reproduce. They exist only to prevent the radar from collapsing into common patterns such as generic chatbots, agents, RAG, and tools.

Anti-bias rules:

- research the selected segment independently before considering any anchor;
- never cite an anchor as evidence for a new opportunity;
- do not copy its actor, process, architecture, or technology combination unless current research independently leads there;
- deliberately consider software without AI, physical devices, edge workloads, optimization, data platforms, security, integrations, and new operating models;
- prefer a materially different process when recent opportunities already use the same dominant pattern;
- judge originality by the process change and value created, not by the novelty of a model or Azure service.

## Round-robin segment rotation

Each watcher run processes one enabled segment from `radar-config.yaml`.

1. Read `radar-state.yaml` and select `current_segment_index`.
2. Read existing opportunities for that segment.
3. Review its `next_focus`, previous search themes, and recent history.
4. Research current real-world problems and solution patterns.
5. Check semantic duplication against all existing opportunities.
6. Publish at most one new opportunity when evidence and fit are sufficient.
7. A run may finish with `no-new-fit`; weak ideas must not be forced.
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
- plausible metrics for measuring value;
- material risks and constraints;
- a macro architecture in Mermaid;
- a fit score with dimension-level reasoning;
- duplicate keys and related opportunities.

Reject generic ideas such as `AI chatbot for HR` without defining the user, process, source data, boundaries, integrations, and measurable outcome.

## Fit score

The symbolic fit score is a decision aid, not a financial forecast.

| Dimension | Range | Meaning |
| --- | ---: | --- |
| Problem evidence and relevance | 0–20 | Strength, recurrence, and urgency of the problem evidence |
| Business or operational value | 0–20 | Potential to improve cost, time, quality, risk, revenue, or capacity |
| Technical feasibility | 0–20 | Data availability, integration feasibility, maturity, and delivery realism |
| Reuse potential | 0–20 | Applicability across multiple organizations or repeated internal contexts |
| Strategic differentiation | 0–20 | Advantage beyond a commodity implementation or simple manual automation |

Record separately:

- `confidence`: low, medium, or high;
- `complexity`: small, medium, large, or research;
- `horizon`: short, medium, or long;
- `azure_fit`: none, low, medium, or high;
- `ai_dependency`: none, optional, supporting, or core;
- `risk`: low, medium, high, or regulated.

A high fit score does not cancel regulatory, privacy, safety, or integration risk.

## Gains and metrics

Do not invent percentage improvements. Describe possible gains and propose metrics such as:

- cycle time;
- manual effort per case;
- rework or error rate;
- service-level compliance;
- escalation rate;
- loss, waste, downtime, or fraud avoided;
- throughput or capacity;
- model or recommendation acceptance rate;
- grounded-answer or extraction quality;
- cost per transaction;
- user or customer satisfaction.

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
- `capability_keys` for major technical capabilities;
- `research_queries` already used;
- `related_opportunities`;
- a concise uniqueness statement.

Before publishing, compare these fields and the full problem statement against the complete index. Similar technologies are allowed when they solve materially different processes. Different wording for the same process is not a new opportunity.

## Relationship to Azure Reference Kit

For each opportunity, classify repository alignment:

- `reuse-existing`: the current kit already contains most required capabilities;
- `extend-kit`: the opportunity reveals useful missing building blocks or references;
- `new-solution`: it can compose existing and new blocks into a reference solution;
- `outside-current-kit`: valuable but better treated as an independent product, experiment, or architecture study.

The repository relationship is descriptive. It must not reduce the opportunity score merely because the kit does not yet support it.
