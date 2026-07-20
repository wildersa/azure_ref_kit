# AGENTS.md — Solution Opportunity Radar

These instructions apply to `docs/opportunities/` and override broader repository guidance when executing the Solution Opportunity Radar.

## Discovery order

Use this sequence:

```text
simulate the actor and workflow
→ expose decisions, exceptions, uncertainty, handoffs, and degraded conditions
→ test deterministic process and software alternatives
→ formulate candidate intelligent interventions
→ research Brazilian relevance, regulation, technical plausibility, and existing solutions
→ publish, extend, integrate, adopt, or record no-new-fit
```

Do not begin with vendor products, market reports, familiar AI patterns, or web-search themes and then invent a matching workflow.

## Operational simulation

Before broad web research:

- choose a concrete organization archetype and actor;
- bound one operational activity from trigger to outcome;
- simulate normal, exception, and peak or degraded flows;
- trace information, systems, decisions, handoffs, waiting, rework, errors, and feedback;
- label assumptions and synthetic events explicitly;
- derive multiple candidate opportunity points from the simulation.

Before keeping an AI candidate, test whether process redesign, integration, forms, rules, search, analytics, dashboards, alerts, queues, or ordinary automation solve it adequately.

## Research role

Research follows initial simulation and candidate generation. Use it to:

- validate the load-bearing Brazilian problem;
- confirm current Brazilian regulation or official guidance;
- validate or contradict simulation assumptions;
- verify technical plausibility and limitations;
- identify existing platforms, products, roadmaps, APIs, tenders, and mature open source;
- prevent duplicate or weakly differentiated opportunities.

Do not require a citation for every simulated micro-step. Do require sources for load-bearing problem claims, regulation, market scale, existing-solution capabilities, roadmaps, and demonstrated outcomes.

## Publication

Follow `watcher-contract.md`, `radar-config.yaml`, and `opportunity-template.md`.

Every active opportunity must include:

- a concrete operational simulation;
- explicit assumptions;
- a material decision, exception, uncertainty, or coordination gap;
- existing-product and non-AI baselines;
- existing-solution landscape and differentiation;
- a material intelligent capability mapped to the process;
- a bounded prototype and measurable failure, redesign, and scale criteria.

Failure of external research to suggest an idea is not a valid `no-new-fit` reason.
