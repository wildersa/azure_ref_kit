# Solution Opportunity Radar

This area tracks AI-enabled solution opportunities derived from **simulated business and operational work** across Brazilian market segments.

The radar is broader than the current Azure Reference Kit catalog. Every active opportunity must include a material intelligent capability, but conventional software, integration, deterministic controls, hardware, and human review may form most of the architecture.

## Purpose

The radar discovers **credible, differentiated, testable hypotheses** by acting like an operational observer:

1. choose a real actor and bounded activity;
2. simulate how the work proceeds under normal, exception, and degraded conditions;
3. expose decisions, uncertainty, delays, rework, handoffs, and missed outcomes;
4. test whether ordinary software or process improvement is sufficient;
5. formulate candidate intelligent interventions for the remaining gaps;
6. use external research to validate relevance, regulation, plausibility, and novelty;
7. define a bounded prototype and measurable comparison.

It is not:

- a procurement approval process;
- a vendor catalog;
- a market-report summarizer;
- a requirement for an existing Brazilian production deployment;
- proof of ROI;
- an implementation backlog by default.

## Core principle

```text
operational simulation
→ decision, exception, uncertainty, or coordination gap
→ deterministic baseline test
→ candidate intelligent intervention
→ Brazilian problem and regulatory validation
→ existing-solution novelty check
→ bounded prototype and measurable comparison
→ risks, controls, confidence, and fit
```

Research follows the initial simulation. It validates or contradicts the hypothesis; it must not become the only source of ideas.

## Files

```text
docs/opportunities/
├─ README.md
├─ watcher-contract.md
├─ radar-config.yaml
├─ radar-state.yaml
├─ opportunity-index.yaml
├─ opportunity-index.md
├─ opportunity-template.md
├─ history.jsonl
└─ segments/
```

## Operational simulation method

Each round selects a concrete organization and actor archetype in the current segment.

The simulation must define:

- organization type and approximate size;
- actor role and decision authority;
- bounded process, trigger, objective, and completion condition;
- inputs, systems, documents, devices, data, and physical context;
- rules, deadlines, cost, safety, and regulatory constraints;
- upstream and downstream handoffs.

At minimum, trace:

### Normal flow

Routine work with expected data, expected system behavior, and ordinary staffing.

### Exception flow

Incomplete, contradictory, unusual, ambiguous, or high-risk inputs that require judgment or escalation.

### Peak or degraded flow

Volume spikes, staff shortage, system delay, equipment degradation, communication loss, deadline pressure, or another operating stressor.

For each scenario, identify:

- information available at each step;
- manual actions and system interactions;
- decisions and judgment calls;
- uncertainty and missing context;
- queues, handoffs, waiting, re-entry, and reconciliation;
- errors, false alarms, missed cases, rework, loss, delay, safety, or service consequences;
- outcomes and corrections that may become labels, feedback, rewards, or evaluation signals.

Simulated details are not facts. The brief must label assumptions and synthetic events explicitly.

## Candidate generation

Candidate interventions must be derived from the simulated process before broad product or market searches.

Useful questions include:

- What must the actor recognize or extract from noisy information?
- What future event, demand, failure, duration, or outcome must be predicted?
- Which cases, actions, resources, or inspections must be ranked?
- Which constrained plan, schedule, route, allocation, or control policy must be optimized?
- Which knowledge must be retrieved and grounded in a decision?
- Which multimodal evidence must be compared?
- Is there a real multi-step goal requiring a governed agent and tools?

Before accepting an AI candidate, test whether the same gap is adequately solved by:

- process redesign;
- forms and mandatory structured fields;
- system integration;
- deterministic rules;
- search and filters;
- analytics or dashboards;
- alerts, queues, or workflow automation.

A strong deterministic solution is the preferred answer when it closes the gap.

## Role of external research

Research is required after candidate generation to:

- confirm the load-bearing problem is current in Brazil;
- verify Brazilian regulation or official operating guidance;
- validate or challenge simulation assumptions;
- find existing official, commercial, sector, roadmap, API, tender, and open-source solutions;
- support technical plausibility;
- identify failures, false positives, adoption barriers, and costs;
- narrow scope and define prototype failure criteria.

Do not require a citation for every simulated micro-step. Require evidence for:

- the load-bearing Brazilian problem;
- regulatory and legal claims;
- market and operating-scale claims;
- existing-solution capabilities and roadmaps;
- claims of demonstrated outcomes.

Every active opportunity needs at least one load-bearing Brazilian source published or materially updated within the previous 18 months. Regulated opportunities also need current Brazilian official or regulatory context.

## Existing-solution guardrail

The radar must not present an existing solution as a new opportunity.

Review, when relevant:

- official and regulator platforms;
- government systems and roadmaps;
- commercial and sector products;
- recent launches and announced capabilities;
- APIs and extension points;
- public tenders and procurement records;
- maintained open-source solutions.

Choose one disposition:

- `build`: no adequate current solution covers the specific gap;
- `extend`: an existing platform needs a material differentiated capability;
- `integrate`: value comes from connecting existing systems around a distinct gap;
- `adopt`: the current need is adequately addressed;
- `no-new-fit`: no separate differentiated opportunity remains.

Changing cloud, model vendor, architecture, or UI is not differentiation. Generic RAG, clustering, dashboards, agents, or ranking are not differentiation unless they change a material process or measurable outcome.

## Intelligent-capability requirement

Every active opportunity requires at least one material model-based capability with `ai_dependency: supporting|core`, such as:

- model training or fine-tuning;
- generative AI with grounding and evaluation;
- governed agents and tool use;
- RAG;
- speech, image, video, or document recognition;
- classification, extraction, ranking, or recommendation;
- anomaly detection, prediction, or forecasting;
- optimization or reinforcement learning;
- multimodal inference.

A chat box, summary button, generic copilot, or optional assistant added to an unchanged workflow does not qualify.

Every opportunity must define:

- the exact process stage and decision where intelligence enters;
- inputs and outputs;
- training, grounding, simulation, inference, or optimization assumptions;
- evaluation metrics;
- fallback, abstention, deterministic validation, rollback, and human review.

## Evidence model

Separate:

- **simulated observation:** a workflow-derived assumption;
- **problem evidence:** confirms current pain, delay, risk, loss, interruption, or unmet need;
- **existing-solution evidence:** confirms what is available or planned;
- **favorable evidence:** supports plausibility of the uncovered intervention;
- **counter-evidence:** failures, limitations, false alerts, adoption issues, cost, or strong alternatives;
- **inference:** reasoned implication not directly proven;
- **unknowns:** facts requiring observation, customer data, prototype, pilot, integration test, or legal review.

Counter-evidence normally changes scope, confidence, controls, or failure criteria. It is not automatically a rejection.

## Simulation breadth

Before returning `no-new-fit`, the watcher must simulate at least three materially different workflows or scenario variants when the segment supports them.

Vary:

- actor and authority;
- front-office, back-office, field, physical, analytical, or supervisory work;
- normal, exception, peak, degraded, safety, and recovery conditions;
- organization size and maturity;
- structured, text, document, image, speech, event, sensor, spatial, graph, and time-series data;
- batch, synchronous, asynchronous, mobile, edge, and human-in-the-loop interaction.

The requirement is not “three search themes.” It is three believable operational views.

## Opportunity quality gate

Publish only when the opportunity contains:

- a concrete operational simulation with explicit assumptions;
- a specific actor, process, and current Brazilian problem;
- at least one material decision, exception, uncertainty, or coordination gap;
- a deterministic baseline test;
- an existing-solution landscape and explicit `build|extend|integrate` disposition;
- a material uncovered gap and differentiation statement;
- a necessary intelligent capability;
- a plausible data, feedback, integration, or simulation path;
- a bounded prototype;
- model, workflow, business, adoption, and safety metrics;
- failure, redesign, and scale criteria;
- risks, controls, fit rationale, duplicate keys, and uniqueness statement.

Production deployment, proven ROI, known local error rates, completed integration, and demonstrated adoption are not requirements for a `hypothesis`.

## Valid `no-new-fit`

Use `no-new-fit` only after adequate simulation and novelty research when:

- no current Brazilian evidence supports any load-bearing simulated problem;
- all viable candidates duplicate repository opportunities;
- an existing solution covers the actor, process, capability, and outcome without a material gap;
- adoption or configuration is sufficient;
- deterministic software or process improvement is sufficient;
- AI is decorative or unnecessary;
- no plausible data, feedback, model, integration, simulation, or prototype path exists;
- the central mechanism is invalidated without mitigation;
- no candidate can be narrowed to a concrete actor, process, and measurable outcome.

Failure of external research to suggest an idea is not a valid `no-new-fit` reason.

## Fit score

The fit score is a discovery aid, not a financial forecast.

| Dimension | Range | Meaning |
| --- | ---: | --- |
| Process-opportunity fit | 0–20 | Materiality and specificity of the simulated decision, exception, uncertainty, or coordination gap |
| Business or operational value | 0–20 | Plausible value if the intervention works |
| Technical feasibility | 0–20 | Whether a bounded prototype can be built and meaningfully tested |
| Reuse potential | 0–20 | Applicability across repeated workflows or organizations |
| Strategic differentiation | 0–20 | Uncovered capability or outcome beyond existing solutions and deterministic automation |

Record confidence, complexity, horizon, risk, solution evidence, operational maturity, Azure fit, and AI dependency separately.

## Status and boundaries

```text
hypothesis → researched → shortlisted → approved → implementing → implemented
```

Alternative states: `rejected`, `superseded`, and `parked`.

The watcher may create and update opportunities, indexes, state, and history. It must not open implementation issues, add runtime code, or approve implementation without explicit human direction.
