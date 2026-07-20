# Solution Opportunity Watcher Contract

## Goal

Execute one evidence-based discovery round for the current business segment and maintain the Solution Opportunity Radar.

The radar discovers **credible, differentiated, testable solution hypotheses**. It is not a procurement gate and does not require an existing Brazilian production deployment, proven ROI, completed integration, clean labels, or demonstrated adoption before publishing a hypothesis.

It also must not present an already available platform, product, official roadmap capability, or mature open-source solution as a new opportunity.

Every active opportunity must include:

- a current and specific Brazilian problem;
- a defined actor and operational process;
- a current existing-solution landscape;
- a material gap or distinct outcome not already delivered;
- a material intelligent capability;
- an explicit explanation of where each AI component enters;
- a plausible data and integration path;
- a bounded prototype or experiment;
- assumptions, risks, counter-evidence, failure criteria, and human controls.

## Core decision rule

```text
problem evidence proves that the opportunity matters
existing-solution research proves whether it is actually an opportunity
solution evidence changes confidence and maturity
prototype design proves that the remaining hypothesis is testable
```

A known solution does not automatically eliminate every adjacent opportunity. It changes the required framing:

- **build:** no adequate current solution covers the defined gap;
- **extend:** an existing platform should receive a clearly differentiated capability;
- **integrate:** value comes from connecting existing systems or models around a distinct process gap;
- **adopt:** the need is already adequately addressed and the correct recommendation is adoption, not a new opportunity;
- **no-new-fit:** the candidate substantially duplicates an existing solution without a material uncovered gap.

## Default market and date context

The default market and jurisdiction are **Brazil**, evaluated at the actual execution date.

Every run must:

- use the real execution date and absolute dates;
- research in Portuguese and English, with Brazil-specific queries first;
- prove that the problem exists or is materially applicable in Brazil;
- prefer current Brazilian regulators, public institutions, official statistics, industry associations, public tenders, operational reports, and credible local cases;
- use current Brazilian rules or operating guidance for regulated sectors;
- distinguish publication date, data period, rule-effective date, roadmap date, launch date, and current validity.

At least one load-bearing Brazilian problem source published or materially updated within the previous 18 months is required. Regulated opportunities also require a current Brazilian official or regulatory source.

Foreign evidence may support technical plausibility, architecture, limitations, failures, or existing-solution comparison. It must not define Brazilian law, liability, reimbursement, market structure, or operating assumptions.

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
2. Review recent history and existing repository opportunities.
3. Research at least three materially different current Brazilian problem themes when sources are available.
4. Select the strongest specific problem with a plausible material intelligent capability.
5. Search the current solution landscape before drafting: official platforms, regulator or government systems, vendor products, sector platforms, startups, public roadmaps, recent launches, public tenders, reference implementations, and mature open source.
6. Compare actor, process, inputs, outputs, intelligent mechanism, integrations, authority, and measured outcome against existing solutions.
7. Decide `build`, `extend`, `integrate`, `adopt`, or `no-new-fit`.
8. Research comparable successes, limitations, failures, cancellations, and conventional alternatives.
9. Separate confirmed problem evidence, existing-solution facts, favorable solution evidence, counter-evidence, inference, and unknowns.
10. Define the baseline, differentiated gap, required data, bounded prototype, AI role map, and validation criteria.
11. Check semantic duplication against the repository and external solution landscape.
12. Publish at most one differentiated opportunity, normally as `hypothesis`.
13. Update the full document, active indexes, history, segment state, `next_focus`, and cursor.
14. Commit documentation changes directly to `main`.

## Search breadth

Do not evaluate one generic theme and declare the segment empty. Vary:

- actor and process;
- problem family;
- company or institution size;
- data type and integration shape;
- model family and intelligent technique;
- software, edge, hardware-assisted, multimodal, optimization, simulation, or agent architecture.

## Mandatory existing-solution landscape

Before publication, search current solutions using the exact actor and process plus terms such as:

- plataforma, sistema, software, produto, serviço, inteligência artificial, automação, lançamento, roadmap, piloto, API, edital, fornecedor;
- platform, product, software, solution, AI, automation, launch, roadmap, API, procurement, vendor, open source.

Prefer official product documentation, regulator or government pages, release notes, current roadmaps, API documentation, public procurement records, and maintained repositories over generic market articles.

Every brief must include an `Existing solutions and differentiation` section with:

- **Existing solutions reviewed:** name, owner/vendor, current date, and evidence;
- **Current capabilities:** what each solution already performs;
- **Overlap:** actor, process, capability, integration, and outcome already covered;
- **Uncovered gap:** precise missing capability or underserved context;
- **Disposition:** build | extend | integrate | adopt | no-new-fit;
- **Differentiation statement:** why the candidate is not merely a renamed existing solution.

Apply these rules:

- an existing solution covering the same actor, process, central capability, and outcome invalidates a `new-solution` framing;
- a roadmap or recently launched capability counts as existing landscape even when rollout is incomplete;
- changing the cloud provider, model vendor, UI, or architecture does not create a new opportunity;
- adding generic clustering, dashboards, RAG, an agent, or a ranking layer is not differentiation unless it changes a material process or measurable outcome;
- an extension is valid only when the uncovered gap is specific, evidenced, and testable;
- when adoption of an existing solution is the reasonable answer, record `no-new-fit` rather than designing a duplicate.

## Evidence discipline

Distinguish:

- **problem evidence:** proves the pain, cost, delay, risk, interruption, or unmet need;
- **existing-solution evidence:** proves what is already available or planned;
- **favorable solution evidence:** supports technical or operational plausibility for the uncovered gap;
- **counter-evidence:** failures, weak accuracy, false alerts, adoption problems, unexpected cost, or effective simpler alternatives;
- **inference:** reasoned but not directly proven;
- **unknowns:** facts requiring customer data, prototype, pilot, integration test, or legal review.

Counter-evidence is primarily a design input. Reject only when it invalidates the central mechanism without a credible bounded mitigation.

## Mandatory AI role explanation

Every active opportunity must contain a `Where AI enters` section. For every intelligent component, identify:

- process stage;
- component and primary role;
- model family;
- inputs and outputs;
- training or grounding requirement and cadence;
- inference location and runtime mode;
- deterministic and human controls.

Do not use `AI`, `agent`, `LLM`, and `model` as synonyms. State `Agent: not used` and `LLM: not used` when applicable. Identify APIs, databases, rules, calculations, queues, dashboards, orchestration, and approvals as non-AI when they are deterministic.

The macro architecture must name actual model roles, not a generic `AI` box.

## Prototype discipline

Every opportunity must define:

- the current manual or system process;
- the strongest realistic non-AI and existing-product baseline;
- the exact differentiated context where intelligence may add value;
- data owners, access, coverage, labels or feedback, privacy, drift, and integration assumptions;
- a narrow prototype or experiment;
- model, business, workflow, adoption, and safety metrics;
- stop, redesign, and scale criteria.

Technical feasibility means prototype feasibility and testability, not proven production success.

## Opportunity quality gate

Publish only when the brief includes:

- specific actor, process, Brazilian problem, and current evidence;
- current existing-solution landscape;
- explicit build/extend/integrate disposition;
- material uncovered gap and differentiation statement;
- material intelligent capability and complete AI role map;
- plausible data and integration path;
- baseline comparison;
- favorable evidence, counter-evidence, inference, and unknowns;
- bounded prototype and measurable validation plan;
- named macro architecture;
- risks, controls, fit rationale, duplicate keys, and uniqueness statement.

## Valid `no-new-fit` reasons

Record `no-new-fit` when one or more are true after adequate search breadth:

- no current Brazilian evidence supports a specific problem;
- all credible findings duplicate repository opportunities;
- a current official, commercial, sector, or open-source solution already covers the actor, process, central capability, and outcome without a material evidenced gap;
- adoption or extension of an existing platform is sufficient and no separate prototype opportunity remains;
- the intelligent capability is decorative or unnecessary;
- no plausible data, model, integration, simulation, or prototype path exists;
- the central mechanism is invalidated without credible mitigation;
- the candidate cannot be narrowed to a concrete actor, process, and measurable outcome.

Do not reject merely because production evidence, ROI, local metrics, clean labels, completed integration, or adoption proof are unavailable.

## Repository actions and boundaries

The watcher may create, update, reject, supersede, and remove opportunity records from the active indexes. Rejected records may remain in segment folders for audit.

It must not:

- open implementation issues;
- create implementation branches or pull requests;
- add runtime code or infrastructure;
- mark an opportunity `approved` without explicit human decision;
- convert a high score directly into implementation backlog.