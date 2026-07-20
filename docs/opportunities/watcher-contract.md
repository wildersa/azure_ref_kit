# Solution Opportunity Watcher Contract

## Goal

Execute one discovery round for the current business segment and maintain the Solution Opportunity Radar.

The radar discovers **credible, differentiated, testable solution hypotheses by simulating real work**. External research validates context, regulation, plausibility, and novelty; it is not the primary idea generator.

The radar is not a procurement gate. It does not require an existing Brazilian production deployment, proven ROI, completed integration, clean labels, published local model metrics, or demonstrated adoption before publishing a hypothesis.

It must not present an already available platform, product, official roadmap capability, or mature open-source solution as a new opportunity.

## Core discovery order

```text
simulate a real actor performing a bounded process
→ expose decisions, uncertainty, exceptions, handoffs, delay, rework, and failure modes
→ identify where deterministic software is sufficient
→ formulate several candidate intelligent interventions
→ research Brazilian relevance, regulation, technical plausibility, and existing solutions
→ select, narrow, extend, integrate, adopt, or reject
→ define a bounded prototype and measurable comparison
```

Do not reverse this order by beginning with vendor products, market reports, AI patterns, or search-result themes and then inventing a matching workflow.

## Operational simulation is the primary discovery engine

Before broad web research, select a concrete operating archetype in the current segment:

- organization type and approximate size;
- primary actor or role;
- bounded process, trigger, objective, and completion condition;
- inputs, systems, documents, devices, data, and physical context;
- rules, deadlines, authority, safety, cost, and compliance constraints;
- handoffs to other roles or systems.

Simulate the process independently of a proposed solution. At minimum, cover:

1. **normal flow:** routine work with expected inputs;
2. **exception flow:** incomplete, contradictory, unusual, or ambiguous input;
3. **peak or degraded flow:** volume spike, staff shortage, system delay, equipment degradation, deadline pressure, or disrupted operation.

For each scenario, trace:

- trigger and expected outcome;
- actor actions and system interactions;
- information available at each step;
- decisions and judgment calls;
- uncertainty and missing context;
- queues, handoffs, waiting, re-entry, duplication, and manual reconciliation;
- errors, false alarms, missed cases, rework, loss, delay, safety, or service impact;
- feedback that could become a label, reward, correction, or evaluation signal.

The simulation may use sector knowledge, synthetic events, and explicit assumptions. Mark simulated assumptions as assumptions; do not present them as sourced facts.

The watcher must first ask:

```text
Where does this actor repeatedly need to recognize, interpret, predict, rank,
recommend, optimize, generate, retrieve, or act under uncertainty?
```

Then ask:

```text
Would rules, forms, integration, search, analytics, or workflow automation solve it adequately?
```

Only the remaining material gaps are AI candidates.

## Required repository sources

Read before each run:

- `AGENTS.md`
- `docs/opportunities/README.md`
- `docs/opportunities/radar-config.yaml`
- `docs/opportunities/radar-state.yaml`
- `docs/opportunities/opportunity-index.yaml`
- `docs/opportunities/opportunity-template.md`
- recent relevant entries from `docs/opportunities/history.jsonl`

Use the index first. Open full opportunity documents only for plausible duplication or useful comparison.

## One-run workflow

1. Read the current round-robin segment and `next_focus`.
2. Review recent history and existing repository opportunities.
3. Choose one or more concrete organization and actor archetypes.
4. Simulate at least three materially different workflows or scenario variants before `no-new-fit`.
5. Record decisions, uncertainty, bottlenecks, exceptions, failure modes, feedback signals, and deterministic alternatives.
6. Generate several candidate interventions from the simulation before broad web searches.
7. Eliminate candidates where integration, rules, forms, search, dashboards, or ordinary automation are sufficient.
8. Research current Brazilian evidence for the remaining problems and regulated context.
9. Research current official, commercial, sector, roadmap, API, and open-source solutions as a novelty guardrail.
10. Compare actor, process, inputs, outputs, intelligent mechanism, integration, authority, and measurable outcome.
11. Decide `build`, `extend`, `integrate`, `adopt`, or `no-new-fit`.
12. Research favorable patterns, limitations, failures, cancellations, costs, and counter-evidence.
13. Define data assumptions, AI role map, prototype, baselines, controls, and measurable validation.
14. Publish at most one opportunity, normally as `hypothesis`.
15. Update the complete document, active indexes, history, segment state, `next_focus`, and cursor.
16. Commit documentation changes directly to `main`.

## Simulation breadth

Before `no-new-fit`, cover at least three materially different workflow simulations or scenario variants when a segment supports them.

Vary at least some of:

- actor and decision authority;
- front-office, back-office, field, physical, analytical, or supervisory work;
- normal, exception, peak, degraded, safety, and recovery conditions;
- organization size and operating maturity;
- structured, unstructured, visual, speech, event, sensor, spatial, graph, or time-series data;
- synchronous, asynchronous, batch, edge, mobile, document, and human-in-the-loop interaction.

The objective is not three web-search themes. The objective is three believable operational views that can expose different opportunity points.

## Role of external research

Research is required, but it follows candidate generation.

Use it to:

- validate that the load-bearing problem is current and relevant in Brazil;
- confirm current Brazilian regulation or official operating guidance;
- verify that assumed workflows are plausible;
- find existing solutions, releases, roadmaps, APIs, tenders, and open-source alternatives;
- support technical plausibility;
- discover failures, false positives, adoption issues, and cost constraints;
- narrow scope and define prototype failure criteria.

Do not require a citation for every simulated micro-step. Require evidence for the load-bearing problem, regulatory claims, market claims, existing-solution capabilities, and claims of demonstrated outcomes.

At least one load-bearing Brazilian problem source published or materially updated within the previous 18 months is required for an active opportunity. Regulated opportunities also require current Brazilian official or regulatory context.

Foreign evidence may support technical plausibility, architecture, limitations, failures, or comparison. It must not define Brazilian law, liability, reimbursement, market structure, or operating assumptions.

## Mandatory existing-solution landscape

Existing-solution research is a **novelty and positioning guardrail**, not the discovery engine.

Before publication, review relevant:

- official and regulator platforms;
- government systems and roadmaps;
- commercial and sector products;
- recent releases and announced capabilities;
- APIs and extension points;
- public tenders and procurement records;
- maintained open-source solutions.

Every brief must state:

- **Existing solutions reviewed** and evidence dates;
- **Current capabilities** already delivered;
- **Overlap** with the simulated candidate;
- **Material uncovered gap**;
- **Disposition:** build | extend | integrate | adopt | no-new-fit;
- **Differentiation statement** tied to process and measurable outcome.

Apply these rules:

- an existing solution covering the same actor, process, central capability, and outcome invalidates a `new-solution` framing;
- a roadmap or recently launched capability counts as existing landscape;
- changing cloud, model vendor, UI, or architecture is not differentiation;
- generic clustering, dashboards, RAG, agents, or ranking are not differentiation by themselves;
- an extension is valid when the simulation exposes a specific, material, testable gap;
- when adoption or configuration is sufficient, record `no-new-fit`.

## Evidence discipline

Separate:

- **simulated observation:** a workflow assumption or consequence derived from the operational simulation;
- **problem evidence:** proves current pain, cost, delay, risk, interruption, or unmet need;
- **existing-solution evidence:** proves what is available or planned;
- **favorable evidence:** supports plausibility of the uncovered intervention;
- **counter-evidence:** failures, weak accuracy, false alerts, adoption problems, unexpected cost, or effective simpler alternatives;
- **inference:** reasoned implication not directly proven;
- **unknowns:** facts requiring customer data, prototype, pilot, integration test, or legal review.

Counter-evidence is primarily a design input. Reject only when it invalidates the central mechanism without a credible bounded mitigation.

## Mandatory AI role explanation

Every active opportunity must contain a `Where AI enters` section. For every intelligent component, identify:

- process stage;
- component and primary role;
- model family;
- inputs and outputs;
- training, grounding, simulation, or optimization requirement and cadence;
- inference location and runtime mode;
- deterministic and human controls.

Do not use `AI`, `agent`, `LLM`, and `model` as synonyms. State `Agent: not used` and `LLM: not used` when applicable. Identify APIs, databases, rules, calculations, queues, dashboards, orchestration, and approvals as non-AI when deterministic.

The macro architecture must name actual model roles and show the simulated operational workflow or existing platform being changed.

## Prototype discipline

Every opportunity must define:

- the simulated current process and scenario variants;
- the strongest existing-product and non-AI baselines;
- the exact decision, exception, or uncertainty where intelligence may add value;
- data owners, access, coverage, labels, feedback, simulation, privacy, drift, and integration assumptions;
- a narrow prototype or experiment;
- model, business, workflow, adoption, safety, and incremental-value metrics;
- stop, redesign, and scale criteria.

Technical feasibility means prototype feasibility and testability, not proven production success.

## Opportunity quality gate

Publish only when the brief includes:

- a concrete operational simulation with explicit assumptions;
- specific actor, process, Brazilian problem, and current evidence;
- at least one material decision, exception, or uncertainty not adequately solved by deterministic automation;
- current existing-solution landscape;
- explicit build, extend, or integrate disposition;
- material uncovered gap and differentiation statement;
- material intelligent capability and complete AI role map;
- plausible data, integration, feedback, or simulation path;
- existing-product and non-AI baseline comparison;
- bounded prototype and measurable validation plan;
- risks, counter-evidence, controls, fit rationale, duplicate keys, and uniqueness statement.

## Valid `no-new-fit` reasons

Record `no-new-fit` only after adequate operational simulation and novelty research when one or more are true:

- no current Brazilian evidence supports any specific load-bearing problem exposed by the simulations;
- all credible simulated opportunities duplicate repository opportunities;
- a current official, commercial, sector, or open-source solution covers the actor, process, central capability, and outcome without a material gap;
- adoption or configuration is sufficient and no separate prototype remains;
- deterministic software or process improvement adequately solves the exposed problem;
- the intelligent capability is decorative or unnecessary;
- no plausible data, model, integration, feedback, simulation, or prototype path exists;
- the central mechanism is invalidated without credible mitigation;
- the candidate cannot be narrowed to a concrete actor, process, and measurable outcome.

Do not reject merely because production evidence, ROI, local metrics, clean labels, completed integration, or adoption proof are unavailable.

## Repository actions and boundaries

The watcher may create, update, reject, supersede, and remove opportunity records from active indexes. Rejected records may remain for audit.

It must not:

- open implementation issues;
- create implementation branches or pull requests;
- add runtime code or infrastructure;
- mark an opportunity `approved` without explicit human decision;
- convert a high score directly into implementation backlog.
