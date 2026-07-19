# Solution Opportunity Radar

This area tracks current Brazilian business and operational problems that may justify AI-enabled software, data, automation, integration, machine learning, recognition, prediction, optimization, agents, or related solutions.

The radar is intentionally broader than the current Azure Reference Kit catalog. Every published opportunity must include a material intelligent capability, but conventional software, integration, deterministic controls, hardware, and human review may form most of the architecture.

## Purpose

The radar discovers **credible, testable solution hypotheses**.

It is not:

- a procurement approval process;
- a requirement for an existing Brazilian production deployment;
- proof of ROI;
- an implementation backlog by default.

A useful opportunity can be published before production validation when it has:

- a specific current Brazilian problem;
- a defined actor and process;
- a plausible material intelligent capability;
- a realistic data or simulation path;
- a bounded prototype validation plan;
- explicit risks, assumptions, counter-evidence, and human controls.

## Core principle

```text
real Brazilian problem
→ actor and affected process
→ current baseline
→ solution hypothesis
→ material intelligent capability
→ data and integration assumptions
→ bounded prototype and measurable comparison
→ risks, counter-evidence and controls
→ fit and confidence
→ optional human-approved implementation planning
```

Problem evidence proves that the opportunity matters. Solution evidence changes confidence and maturity. Prototype design proves that the hypothesis can be tested.

Lack of production evidence does not reject a hypothesis by itself.

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

## Intelligent-capability requirement

At least one model-based capability must be `supporting` or `core`, such as:

- model training or fine-tuning;
- generative AI with grounding and evaluation;
- governed agents and tool use;
- RAG;
- speech, image, video, or document recognition;
- classification, extraction, ranking, or recommendation;
- anomaly detection, prediction, or forecasting;
- optimization or reinforcement learning;
- multimodal inference.

A chat box, summary button, or optional assistant added to an otherwise unchanged workflow does not qualify.

Every opportunity must define:

- why the intelligent capability matters;
- its inputs and outputs;
- model-use, training, grounding, or optimization assumptions;
- evaluation metrics;
- fallback, abstention, deterministic validation, or human review.

## Evidence model

Separate:

- **problem evidence:** confirms the pain, cost, delay, risk, or interruption;
- **favorable solution evidence:** supports technical or operational plausibility;
- **counter-evidence:** failed pilots, cancellations, limitations, false alerts, adoption problems, cost concerns, or strong conventional alternatives;
- **inference:** reasoned implication not directly proven;
- **unknowns:** facts requiring prototype, pilot, customer data, integration test, or legal review.

Counter-evidence is normally a design input. It can reduce confidence, narrow scope, strengthen human controls, or define prototype failure criteria. It is not automatically a reason to reject the opportunity.

## Prototype-first validation

The opportunity must define:

- the current manual or system baseline;
- the strongest realistic non-AI alternative;
- the context in which intelligence may add incremental value;
- expected data sources, labels or feedback, quality risks, privacy, drift, and integration assumptions;
- a bounded prototype scope;
- model, workflow, business, adoption, and safety metrics;
- failure, redesign, and scale criteria.

Unknown local false-positive rates, integration effort, labels, cost, or adoption belong in the prototype plan. They do not automatically invalidate discovery.

## Search breadth

Each run processes one enabled segment. Before returning `no-new-fit`, the watcher must investigate at least three materially different problem themes when sources are available.

Do not evaluate only one generic pattern and declare the segment empty. Vary:

- actor and process;
- problem family;
- company size and maturity;
- model family and data type;
- software, sensor, edge, document, speech, vision, prediction, ranking, optimization, or agentic architecture.

## Research expectations

Use multiple source types when possible:

1. current Brazilian regulators, institutions, official statistics, and standards;
2. Brazilian industry research, tenders, operational reports, and credible cases;
3. international technical research, standards, and comparable solution patterns;
4. operational guides, incident reports, failure reports, and process documentation;
5. academic and technical research;
6. mature open-source projects and public architectures;
7. reputable reporting.

Marketing claims cannot prove the Brazilian problem. They may be recorded as limited evidence of solution direction when clearly labeled.

## Opportunity quality gate

Publish when the opportunity contains:

- a specific actor, process, company profile, and current Brazilian problem;
- recent Brazilian problem evidence;
- current Brazilian official context when regulated;
- a process-changing solution hypothesis;
- a material intelligent capability;
- a plausible data, model, integration, or simulation path;
- a baseline comparison;
- favorable evidence, counter-evidence, inference, and unknowns;
- a bounded prototype validation plan;
- macro architecture, risks, controls, metrics, and fit rationale;
- duplicate-control keys and a uniqueness statement.

Production deployment, proven ROI, known local error rates, completed integration, and demonstrated employee adoption are not publication requirements for a `hypothesis`.

## Valid `no-new-fit`

Use `no-new-fit` only when:

- no current Brazilian evidence supports a specific problem;
- the candidate duplicates an existing opportunity;
- AI is decorative or unnecessary;
- no plausible prototype path can be defined;
- the central mechanism is invalidated without credible mitigation;
- the idea cannot be narrowed to a concrete actor, process, and measurable outcome.

Do not use `no-new-fit` merely because production validation, ROI, local metrics, labels, integrations, adoption, or cost are still unknown.

## Fit score

The symbolic fit score is a discovery aid, not a financial forecast.

| Dimension | Range | Meaning |
| --- | ---: | --- |
| Problem evidence and relevance | 0–20 | Strength and specificity of current Brazilian evidence |
| Business or operational value | 0–20 | Plausible value if the hypothesis succeeds |
| Technical feasibility | 0–20 | Whether a bounded prototype can be built and meaningfully tested |
| Reuse potential | 0–20 | Applicability across organizations or repeated contexts |
| Strategic differentiation | 0–20 | Material intelligent advantage beyond deterministic automation |

Record separately:

- confidence;
- complexity;
- horizon;
- risk;
- solution evidence level;
- operational maturity;
- Azure fit;
- AI dependency.

Use `confidence: high` and `operational maturity: proven` only with strong production evidence. Lower confidence is valid for publishable prototype hypotheses.

## Status lifecycle

```text
hypothesis
→ researched
→ shortlisted
→ approved
→ implementing
→ implemented
```

Alternative states:

```text
rejected
superseded
parked
```

The watcher may create and update opportunities, indexes, state, and history. It must not open implementation issues or approve implementation without explicit human direction.

## Duplicate prevention

Each opportunity must record:

- `problem_keys`;
- `capability_keys`;
- research queries, including counter-evidence searches;
- related opportunities;
- a concise uniqueness statement.

A different model applied to the same process is not automatically a new opportunity.

## Relationship to Azure Reference Kit

Classify repository alignment as:

- `reuse-existing`;
- `extend-kit`;
- `new-solution`;
- `outside-current-kit`.

Repository alignment is descriptive and must not inflate the fit score.