# Solution Opportunity Watcher Contract

## Goal

Execute one evidence-based research round for the current business segment and maintain the Solution Opportunity Radar without turning weak hypotheses into implementation backlog.

The radar is broader than Azure and broader than the capabilities already present in this repository. However, every published opportunity must include a material intelligent capability: model training, fine-tuning, generative AI, an agent, RAG, recognition, prediction, anomaly detection, recommendation, optimization, reinforcement learning, or another explicit model-based capability.

Conventional software, integrations, workflows, portals, data platforms, hardware, and deterministic controls may form most of the surrounding architecture. They cannot be the complete solution by themselves.

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
3. Research current, concrete problems on the web using multiple source types when possible.
4. Separate confirmed evidence from inference.
5. Check semantic duplication before drafting.
6. Identify an intelligent capability that materially changes the process or outcome and is justified by the researched problem.
7. Create at most one opportunity when the evidence, specificity, intelligent contribution, measurable value, risks, architecture, and fit meet the repository quality gate.
8. A valid run may finish as `no-new-fit`; never force a weak opportunity or bolt AI onto a conventional application.
9. When publishing, create the full document under the correct segment folder and update both `opportunity-index.yaml` and `opportunity-index.md` with one concise description.
10. Append the run result to `history.jsonl`.
11. Update the current segment state, set a different `next_focus`, and advance the round-robin cursor.
12. Commit documentation changes directly to `main` with a focused commit message.

## Research discipline

Prefer evidence in this order when applicable:

1. regulators, public institutions, standards bodies, and official statistics;
2. industry associations and sector research;
3. operational guides, public tenders, incident reports, and process documentation;
4. public customer case studies;
5. academic and technical research;
6. mature open-source projects and public reference architectures;
7. reputable reporting describing a concrete operational problem.

Marketing claims alone are insufficient. Quantified gains require a source or must be labeled as an experiment target.

Do not begin from a preferred technology. Begin from an actor, a recurring process, a concrete interruption or risk, and a measurable consequence. Then determine which intelligent technique is necessary and how normal software, integration, automation, data, hardware, and deterministic controls support it.

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
- credible evidence that the problem exists;
- a process-changing solution rather than a technology label;
- a material intelligent capability meeting the mandatory test above;
- a macro Mermaid architecture;
- possible gains without invented percentages;
- measurable business and model-quality validation metrics;
- material risks, limits, and human-control boundaries;
- fit scoring with dimension-level rationale;
- duplicate-control keys and a uniqueness statement;
- repository alignment that does not influence the fit score;
- an index description of roughly 40 words or fewer.

Reject generic ideas such as `AI chatbot for HR` unless the exact user, process, data, intelligent behavior, boundaries, integrations, evaluation, and measurable outcome are defined.

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

Use the five 0–20 dimensions defined in `radar-config.yaml`. The score is symbolic and must not hide low confidence, high complexity, regulated risk, weak data availability, or an unproven intelligent technique.

The watcher may create and update opportunity documents and radar control files. It must not:

- open implementation issues;
- create implementation branches or pull requests;
- add runtime code or infrastructure;
- mark an opportunity `approved` without an explicit human decision;
- convert an opportunity into backlog merely because its fit score is high.

New opportunities start as `hypothesis` or `researched`, depending on evidence quality.
