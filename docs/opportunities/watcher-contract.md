# Solution Opportunity Watcher Contract

## Goal

Execute one evidence-based research round for the current business segment and maintain the Solution Opportunity Radar without turning weak hypotheses into implementation backlog.

The watcher researches business and operational problems. It is not limited to Azure, artificial intelligence, agents, RAG, or capabilities already present in this repository.

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
6. Create at most one opportunity when the evidence, specificity, measurable value, risks, architecture, and fit meet the repository quality gate.
7. A valid run may finish as `no-new-fit`; never force a weak opportunity.
8. When publishing, create the full document under the correct segment folder and update both `opportunity-index.yaml` and `opportunity-index.md` with one concise description.
9. Append the run result to `history.jsonl`.
10. Update the current segment state, set a different `next_focus`, and advance the round-robin cursor.
11. Commit documentation changes directly to `main` with a focused commit message.

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

Do not begin from a technology. Begin from an actor, a recurring process, a concrete interruption or risk, and a measurable consequence. Consider normal software, integration, workflow automation, analytics, optimization, machine learning, reinforcement learning, generative AI, hardware, edge processing, or combinations only after the problem is clear.

## Opportunity quality gate

Publish only when the opportunity includes:

- a specific segment, company profile, actor, and process;
- credible evidence that the problem exists;
- a process-changing solution rather than a technology label;
- a macro Mermaid architecture;
- possible gains without invented percentages;
- measurable validation metrics;
- material risks, limits, and human-control boundaries;
- fit scoring with dimension-level rationale;
- duplicate-control keys and a uniqueness statement;
- repository alignment that does not influence the fit score;
- an index description of roughly 40 words or fewer.

Reject generic ideas such as `AI chatbot for HR` unless the exact user, process, data, boundaries, integrations, and measurable outcome are defined.

## Diversity and anti-anchoring rules

Actively diversify across consecutive runs:

- company size and operational maturity;
- user and business process;
- solution type and architecture shape;
- interaction model and delivery channel;
- AI dependency;
- complexity and time horizon;
- software-only, hardware-assisted, data, integration, automation, optimization, and research-oriented opportunities.

Do not repeatedly prefer agents, chat interfaces, RAG, document processing, or the repository's existing capabilities.

The few-shot examples in the watcher prompt define only the permitted breadth of solutions. They are not preferred ideas, search queries, templates, scoring references, or target distributions. Research the selected segment independently and do not copy, remix, or prioritize examples because they appear in the prompt.

## Duplicate prevention

Before publishing:

- compare the proposed problem against index titles and short descriptions;
- compare `problem_keys`, `capability_keys`, actor, process, and expected outcome;
- inspect related full documents only when similarity is plausible;
- treat a new technology applied to the same process as a duplicate unless the process or outcome changes materially;
- record `no-new-fit` when all credible findings duplicate existing opportunities.

## Fit and decision boundaries

Use the five 0–20 dimensions defined in `radar-config.yaml`. The score is symbolic and must not hide low confidence, high complexity, or regulated risk.

The watcher may create and update opportunity documents and radar control files. It must not:

- open implementation issues;
- create implementation branches or pull requests;
- add runtime code or infrastructure;
- mark an opportunity `approved` without an explicit human decision;
- convert an opportunity into backlog merely because its fit score is high.

New opportunities start as `hypothesis` or `researched`, depending on evidence quality.