# Solution Opportunity Watcher Contract

## Goal

Execute one evidence-based research round for the current business segment and maintain the Solution Opportunity Radar without turning weak hypotheses into implementation backlog.

The radar is broader than Azure and broader than the capabilities already present in this repository. However, every published opportunity must include a material intelligent capability: model training, fine-tuning, generative AI, an agent, RAG, recognition, prediction, anomaly detection, recommendation, optimization, reinforcement learning, or another explicit model-based capability.

Conventional software, integrations, workflows, portals, data platforms, hardware, and deterministic controls may form most of the surrounding architecture. They cannot be the complete solution by themselves.

The watcher must act as solution due diligence, not as an enthusiastic idea generator. Evidence that a problem is large does not prove that the proposed intelligent solution is feasible, adoptable, or economical.

## Default market and date context

The default target market is **Brazil**, evaluated against the real conditions and current date of each watcher run.

Every run must:

- resolve the actual execution date and use absolute dates in the opportunity;
- research the selected segment in Portuguese and English, with Brazil-specific queries first;
- prove that the problem exists or is materially applicable in Brazil;
- prefer Brazilian regulators, public institutions, official statistics, industry associations, public tenders, operational reports, and credible local case studies;
- use current Brazilian regulation and operating rules for regulated sectors;
- distinguish the publication date, data reference period, rule effective date, and current validity of each important source.

A publishable opportunity requires at least one load-bearing Brazilian source published or materially updated within the previous 18 months. For regulated opportunities, it also requires a current Brazilian regulatory, supervisory, or official operating source. Older sources may explain history or stable concepts but cannot establish current urgency by themselves.

Foreign evidence is secondary. It may support architecture, technical feasibility, comparison, or a pattern that can be adapted, but it must not be the primary proof of the Brazilian problem. Never import a foreign liability rule, reimbursement regime, legal obligation, market structure, acronym, or operating assumption as if it applied in Brazil.

A global opportunity is allowed only when the document explicitly demonstrates its current applicability to Brazilian organizations. If current Brazilian relevance cannot be established, record `no-new-fit`.

## Required repository sources

Read before each run:

- `AGENTS.md`
- `docs/opportunities/README.md`
- `docs/opportunities/radar-config.yaml`
- `docs/opportunities/radar-state.yaml`
- `docs/opportunities/opportunity-index.yaml`
- `docs/opportunities/opportunity-template.md`
- recent relevant entries from `docs/opportunities/history.jsonl`

Use the simple index first. Open full opportunity documents only when they are relevant to duplicate checking or the current segment.

## One-run workflow

1. Read the round-robin cursor and select the current enabled segment.
2. Review the segment's previous focuses, search themes, existing opportunities, and related cross-industry opportunities.
3. Resolve the current date and research current Brazilian problems first, using multiple source types when possible.
4. Confirm Brazil applicability and current regulatory or operational context before using foreign examples.
5. Separate confirmed evidence from inference and separate evidence of the problem from evidence that the proposed solution works.
6. Research comparable implementations, including successful production use, failed pilots, cancellations, rollbacks, accuracy limitations, false positives, adoption problems, and operating-cost concerns.
7. Define the current or non-AI baseline, required data readiness, plausible unit economics, a bounded pilot, and explicit success and kill criteria.
8. Check semantic duplication before drafting.
9. Identify an intelligent capability that materially changes the process or outcome and is justified by the researched problem.
10. Create at most one opportunity when the evidence, specificity, intelligent contribution, measurable value, risks, architecture, Brazil fit, solution feasibility, counter-evidence, and recency meet the repository quality gate.
11. A valid run may finish as `no-new-fit`; never force a weak opportunity, import a foreign-only case, bolt AI onto a conventional application, or treat problem magnitude as proof of solution maturity.
12. When publishing, create the full document under the correct segment folder and update both `opportunity-index.yaml` and `opportunity-index.md` with one concise description.
13. Append the run result to `history.jsonl`.
14. Update the current segment state, set a different `next_focus`, and advance the round-robin cursor.
15. Commit documentation changes directly to `main` with a focused commit message.

## Research discipline

Prefer evidence in this order when applicable:

1. current Brazilian regulators, public institutions, standards bodies, and official statistics;
2. Brazilian industry associations, sector research, public tenders, operational reports, and credible local case studies;
3. current international regulators, standards, and technical research used for comparison or architecture support;
4. operational guides, incident reports, and process documentation;
5. academic and technical research;
6. mature open-source projects and public reference architectures;
7. reputable reporting describing a concrete operational problem.

Marketing claims alone are insufficient. Quantified gains require a source or must be labeled as an experiment target.

Do not begin from a preferred technology. Begin from an actor, a recurring process, a concrete interruption or risk, and a measurable consequence in the Brazilian context. Then determine which intelligent technique is necessary and how normal software, integration, automation, data, hardware, and deterministic controls support it.

## Mandatory solution due diligence

Every candidate must distinguish:

- **problem evidence:** proof that the pain, cost, delay, risk, or interruption exists;
- **solution evidence:** proof that the proposed intelligent capability can improve that process under comparable operating conditions;
- **counter-evidence:** failed pilots, cancellations, discontinued products, rollbacks, weak accuracy, false-alert burden, poor adoption, unexpected operating cost, or a simpler baseline performing adequately;
- **unknowns:** material facts that still require a pilot or customer data.

For the proposed solution pattern, search in Portuguese and English using terms appropriate to the segment, including equivalents of `falhou`, `cancelado`, `descontinuado`, `rollback`, `piloto`, `resultados`, `precisão`, `falso positivo`, `adoção`, `custo operacional`, `failed`, `cancelled`, `discontinued`, `accuracy`, and `false positives`.

The opportunity must include:

- at least one reviewed comparable deployment when public evidence exists;
- favorable and contrary solution evidence, rather than selecting only supportive sources;
- the current manual, deterministic, rules-based, analytics, or conventional-software baseline;
- why the intelligent capability should outperform that baseline;
- data-access, label-quality, coverage, drift, privacy, integration, and feedback-loop readiness;
- the principal cost drivers for capture, hardware, integration, inference, storage, model operations, and human review;
- a narrow pilot population, process slice, baseline or control, success criteria, and explicit kill criteria;
- the operational consequence of false positives, false negatives, abstention, model degradation, and employee rejection.

When no public comparable deployment exists, state that explicitly. Absence of contrary evidence is not proof of success.

Apply these evidence boundaries:

- high confidence requires credible comparable production evidence, realistic data readiness, and no unresolved failure of the same central capability;
- vendor announcements, demonstrations, prototypes, and unmeasured pilots do not establish production feasibility;
- when no comparable production evidence exists, technical feasibility is capped by `radar-config.yaml` and confidence cannot be high;
- when a comparable implementation failed in the same central capability, the opportunity must explain a concrete architectural, scope, data, or operating-model mitigation;
- an unmitigated comparable failure requires rejection or classification as a low-confidence `research-bet` under the score caps in `radar-config.yaml`;
- if a deterministic or manual baseline is likely cheaper and sufficiently effective, record `no-new-fit` unless the opportunity identifies a measurable context in which intelligence materially changes the outcome.

## Mandatory intelligent-capability test

Every published opportunity must satisfy all of these:

- `ai_dependency` is `supporting` or `core`; `none` and `optional` are invalid;
- the document names the model-based capability and why it is necessary;
- it defines the inputs consumed and outputs produced;
- it explains training, fine-tuning, grounding, inference, or optimization behavior when applicable;
- it defines how model quality or policy performance will be evaluated;
- it defines deterministic validation, human review, abstention, rollback, or another safe fallback;
- removing the intelligent capability would materially reduce the solution's value or make the proposed process change incomplete.

Reject a candidate when AI is merely a summary feature, decorative chat interface, optional assistant, or label attached to a conventional workflow.

## Opportunity quality gate

Publish only when the opportunity includes:

- a specific segment, company profile, actor, and process;
- a declared primary market and jurisdiction, normally Brazil;
- recent Brazilian evidence that the problem exists or is materially applicable;
- current Brazilian regulatory or operating context when the segment is regulated;
- separate problem evidence, solution evidence, counter-evidence, and unknowns;
- a reviewed non-AI baseline and a reason the intelligent capability should outperform it;
- a solution-evidence level and operational-maturity classification;
- a realistic data-readiness assessment;
- a bounded pilot, success criteria, kill criteria, and plausible unit-economics hypothesis;
- a process-changing solution rather than a technology label;
- a material intelligent capability meeting the mandatory test above;
- a macro Mermaid architecture;
- possible gains without invented percentages;
- measurable business and model-quality validation metrics;
- material risks, limits, and human-control boundaries;
- fit scoring with dimension-level rationale and all configured caps applied;
- duplicate-control keys and a uniqueness statement;
- repository alignment that does not influence the fit score;
- an index description of roughly 40 words or fewer.

Reject generic ideas such as `AI chatbot for HR` unless the exact user, process, data, intelligent behavior, boundaries, integrations, evaluation, measurable outcome, Brazilian applicability, current evidence, baseline, counter-evidence, and pilot decision rules are defined.

## Diversity and anti-anchoring rules

Actively diversify across consecutive runs:

- company size and operational maturity;
- user and business process;
- intelligent technique and model family;
- solution type and architecture shape;
- interaction model and delivery channel;
- complexity and time horizon;
- software-centric, hardware-assisted, edge, multimodal, data, integration, optimization, training, and research-oriented opportunities.

Do not repeatedly prefer agents, chat interfaces, RAG, document processing, or the repository's existing capabilities. The intelligence requirement does not mean every opportunity should use generative AI.

The few-shot examples in the watcher prompt define only the permitted breadth of solutions. They are not preferred ideas, search queries, templates, scoring references, or target distributions. Research the selected segment independently and do not copy, remix, or prioritize examples because they appear in the prompt.

## Duplicate prevention

Before publishing:

- compare the proposed problem against index titles and short descriptions;
- compare `problem_keys`, `capability_keys`, actor, process, expected outcome, and intelligent technique;
- inspect related full documents only when similarity is plausible;
- treat a new model applied to the same process as a duplicate unless the process, decision, or outcome changes materially;
- record `no-new-fit` when all credible findings duplicate existing opportunities.

## Fit and decision boundaries

Use the five 0–20 dimensions defined in `radar-config.yaml`. The score is symbolic and must not hide low confidence, high complexity, regulated risk, weak data availability, stale evidence, foreign-only applicability, an unproven intelligent technique, or contrary production evidence.

Apply every configured feasibility and total-score cap before publishing. A high problem-evidence score, business value, reuse potential, or strategic differentiation cannot compensate for technical feasibility below the configured boundary.

The watcher may create and update opportunity documents and radar control files. It must not:

- open implementation issues;
- create implementation branches or pull requests;
- add runtime code or infrastructure;
- mark an opportunity `approved` without an explicit human decision;
- convert an opportunity into backlog merely because its fit score is high.

New opportunities start as `hypothesis` or `researched`, depending on evidence quality. `Researched` and `confidence: high` require solution evidence, not only strong evidence of the problem.