# Solution Opportunity Watcher Contract

## Goal

Execute one evidence-based discovery round for the current business segment and maintain the Solution Opportunity Radar.

The radar exists to discover **credible, testable solution hypotheses**. It is not a procurement gate, an investment committee, or a requirement that the solution already be proven in Brazilian production.

Every published opportunity must include:

- a current and specific Brazilian problem;
- a defined actor and operational process;
- a material intelligent capability;
- an explicit explanation of where each AI component enters the process;
- a plausible data and integration path;
- a bounded prototype or experiment;
- explicit assumptions, risks, counter-evidence, and failure criteria.

Conventional software, integration, workflow, hardware, deterministic controls, and human review may form most of the architecture. The intelligent capability must still materially change the process or outcome.

## Core decision rule

```text
problem evidence proves that the opportunity matters
solution evidence changes confidence and maturity
prototype design proves that the hypothesis is testable
```

Lack of a comparable Brazilian production deployment does not justify `no-new-fit` by itself.

A credible problem-grounded proposal may be published as:

- `status: hypothesis`;
- `confidence: low|medium`;
- `solution_evidence_level: conceptual|prototype|pilot`;
- `operational_maturity: unvalidated|early`.

Production evidence is required only for claims such as `confidence: high`, `operational_maturity: proven`, or proven business impact.

## Default market and date context

The default market and jurisdiction are **Brazil**, evaluated at the actual execution date.

Every run must:

- use the real execution date and absolute dates;
- research in Portuguese and English, with Brazil-specific queries first;
- prove that the problem exists or is materially applicable in Brazil;
- prefer current Brazilian regulators, public institutions, official statistics, industry associations, public tenders, operational reports, and credible local cases;
- use current Brazilian rules or operating guidance for regulated sectors;
- distinguish publication date, data period, rule-effective date, and current validity.

At least one load-bearing Brazilian source published or materially updated within the previous 18 months is required. Regulated opportunities also require a current Brazilian official or regulatory source.

Foreign evidence may support technical plausibility, comparable implementations, architecture, limitations, or failures. It must not define Brazilian law, liability, reimbursement, market structure, or operating assumptions.

## Required repository sources

Read before each run:

- `AGENTS.md`
- `docs/opportunities/README.md`
- `docs/opportunities/radar-config.yaml`
- `docs/opportunities/radar-state.yaml`
- `docs/opportunities/opportunity-index.yaml`
- `docs/opportunities/opportunity-template.md`
- recent relevant entries from `docs/opportunities/history.jsonl`

Use the index first. Open full opportunity documents only for plausible duplication or relevant comparison.

## One-run workflow

1. Read the current round-robin segment and its `next_focus`.
2. Review recent history and existing opportunities.
3. Research several current Brazilian problems within the segment; do not stop at the first familiar theme.
4. Select the strongest specific problem with a plausible material intelligent capability.
5. Research solution patterns, comparable successes, limitations, failures, and conventional alternatives.
6. Separate confirmed problem evidence, favorable solution evidence, counter-evidence, inference, and unknowns.
7. Define the current baseline, why intelligence may add value, required data, a bounded prototype, and measurable validation criteria.
8. Build the explicit AI role map required below.
9. Check semantic duplication.
10. Publish at most one opportunity, normally as a grounded hypothesis unless stronger evidence supports higher maturity.
11. Use `no-new-fit` only under the explicit conditions below.
12. Update the complete document, indexes, history, segment state, `next_focus`, and cursor.
13. Commit documentation changes directly to `main`.

## Search breadth requirement

Before concluding `no-new-fit`, investigate at least three materially different problem themes when sources are available.

Vary:

- actor and process;
- problem type, such as quality, defects, exceptions, loss, fraud, delay, safety, compliance, capacity, maintenance, demand, scheduling, inspection, service recovery, or optimization;
- intelligent technique, such as vision, speech, document recognition, prediction, ranking, anomaly detection, optimization, agents, RAG, or multimodal models;
- company size, data type, interaction model, and architecture shape.

Do not test one generic idea such as predictive maintenance, a generic copilot, generic anomaly detection, or generic computer vision and then declare the segment empty.

## Evidence discipline

Distinguish:

- **problem evidence:** proves the pain, cost, delay, risk, interruption, or unmet need;
- **favorable solution evidence:** supports technical or operational plausibility;
- **counter-evidence:** failed pilots, cancellations, weak accuracy, false alerts, adoption problems, unexpected cost, or a simpler alternative performing well;
- **inference:** reasoned but not directly proven;
- **unknowns:** facts requiring customer data, experiment, prototype, pilot, or legal review.

Search for contrary evidence in Portuguese and English and record it when relevant.

Counter-evidence is primarily a design input, not an automatic rejection. It should narrow scope, change data or capture strategy, increase abstention or human review, lower confidence, strengthen the baseline comparison, or define prototype failure criteria.

Reject only when contrary evidence invalidates the same central mechanism and no credible bounded mitigation or alternative formulation remains.

## Mandatory AI role explanation

Every opportunity must contain a `Where AI enters` section that makes the intelligent architecture understandable without relying on generic labels.

The section must include an AI role map with, for every intelligent component:

- process stage where it operates;
- component name;
- primary role: recognition, extraction, classification, anomaly detection, prediction, ranking, recommendation, optimization, reinforcement learning, generation, retrieval, agent/tool use, or multimodal reasoning;
- model family: classical ML, deep learning, computer vision, speech, graph ML, time-series model, embedding/retrieval, LLM/foundation model, multimodal model, optimization solver, RL policy, or another explicit family;
- inputs and outputs;
- training requirement and cadence;
- inference location and runtime mode;
- human or deterministic control.

The watcher must explicitly distinguish:

- **model from agent:** a model predicts or generates; an agent pursues a goal through governed tools and actions;
- **LLM from classical ML:** do not describe classification, forecasting, anomaly detection, graph ranking, vision, or optimization as an LLM unless an LLM actually performs that task;
- **training from inference:** state whether the prototype uses pretrained inference, prompt/RAG, fine-tuning, supervised training, self-supervised training, simulation, optimization, or reinforcement learning;
- **AI from normal software:** rules, APIs, databases, orchestration, search filters, calculations, dashboards, queues, and approvals must be identified as deterministic when they are not model-based.

When no agent is used, say `Agent: not used`. When no LLM is used, say `LLM: not used`. When several intelligent components exist, separate their responsibilities rather than presenting a single generic AI layer.

The macro architecture must name the actual model roles. Do not leave only a generic node called `AI`, `Intelligence`, or `Agent`.

## Baseline and prototype discipline

Every opportunity must define:

- the current manual or system process;
- the strongest realistic deterministic, rules-based, analytics, integration, workflow, or conventional-software baseline;
- the exact context in which intelligence may add incremental value;
- data owners, access path, coverage, labels or feedback, quality risks, privacy, drift, and integration assumptions;
- a narrow prototype or experiment;
- business, model-quality, workflow, and safety metrics;
- stop, redesign, or scale criteria.

A strong non-AI baseline does not automatically invalidate the opportunity. It becomes the comparison target.

Publish when the intelligent capability has a plausible testable advantage in a defined context, even if that advantage has not yet been proven.

## Mandatory intelligent-capability test

Every published opportunity must satisfy all of these:

- `ai_dependency` is `supporting` or `core`;
- the model-based capability is explicitly named;
- its inputs and outputs are defined;
- training, grounding, inference, optimization, or model-use assumptions are described;
- model or policy quality can be evaluated;
- deterministic validation, human review, abstention, rollback, or manual fallback is defined;
- removing the intelligent capability would materially reduce the proposed value.

Reject decorative AI such as an optional summary, chat box, or assistant attached to a workflow that remains equally valuable without it.

## Opportunity quality gate

Publish when the opportunity includes:

- a specific company profile, actor, process, and Brazilian problem;
- recent Brazilian problem evidence;
- current Brazilian regulatory or operating context when applicable;
- a process-changing solution hypothesis;
- a material intelligent capability;
- a complete AI role map;
- a plausible data and integration path;
- a realistic baseline comparison;
- favorable evidence, counter-evidence, inference, and unknowns without pretending certainty;
- a bounded prototype and measurable validation plan;
- a macro Mermaid architecture with named model and optional-agent roles;
- possible gains without invented percentages;
- risks, limits, and human-control boundaries;
- fit scoring with dimension-level rationale;
- duplicate-control keys and a uniqueness statement.

A hypothesis does not need production proof, proven ROI, local model metrics, known false-positive rates, completed OSS integration, or demonstrated employee adoption. Those are prototype questions unless the document claims higher maturity.

## Valid `no-new-fit` reasons

Record `no-new-fit` only when one or more are true after adequate search breadth:

- no current Brazilian evidence supports a specific problem;
- all credible findings duplicate existing opportunities;
- the intelligent capability is decorative or unnecessary;
- no plausible data, model, integration, simulation, or prototype path can be defined;
- the central technical mechanism is contradicted strongly enough that a bounded mitigation is not credible;
- the candidate is generic and cannot be narrowed to a concrete actor, process, and measurable outcome.

Do not record `no-new-fit` merely because:

- there is no Brazilian production deployment;
- no local false-positive rate is published;
- ROI has not been demonstrated;
- labels, integration effort, adoption, or operating cost are still unknown;
- a deterministic baseline exists;
- the solution still requires a prototype.

Those facts reduce confidence, identify unknowns, or shape the experiment.

## Fit and decision boundaries

Use the five 0–20 dimensions in `radar-config.yaml`.

Technical feasibility means **prototype feasibility and testability**, not proven production success. Evaluate whether a bounded implementation can be built and meaningfully compared against a baseline with obtainable data or simulation.

The score must not hide uncertainty, complexity, regulated risk, weak data assumptions, or counter-evidence. However, uncertainty belongs in confidence, maturity, risk, prototype design, and rationale rather than becoming an automatic publication veto.

The watcher may create and update opportunity documents and radar control files. It must not:

- open implementation issues;
- create implementation branches or pull requests;
- add runtime code or infrastructure;
- mark an opportunity `approved` without explicit human decision;
- convert an opportunity into backlog merely because its fit score is high.

New opportunities normally start as `hypothesis`. Use `researched` only when evidence about the solution pattern is materially stronger than conceptual plausibility.