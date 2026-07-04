# JULES_TEMPLATE v17.1 — Azure Reference Kit Spec-to-PR Issue

Use this template to open implementation issues for Jules in `wildersa/azure_ref_kit`.

The rule is:

```text
one roadmap item
→ one bounded issue
→ Jules executes as a senior stack-specific developer
→ complete PR with proof
```

Do not ask Jules to define roadmap, architecture direction, or product sequencing. That belongs to the maintainer and the repository docs.

Jules receives a ready execution demand: exact role, exact docs to consult, exact repository sources, exact outcome, P0 criteria, boundaries, and proof.

## Non-negotiable rules

- One issue = one bounded roadmap item or one bounded follow-up.
- Do not bundle multiple modules, tracks, or solutions in one issue.
- Do not open umbrella issues for Jules.
- Do not rely on prior chat, hidden context, previous issues, or memory.
- Every Azure/Foundry/DevOps issue must include exact Microsoft Learn URLs to consult.
- Include public sample repositories when Jules should inspect/mirror structure conceptually.
- Agent role must be a senior technical execution persona, not only a domain label.
- Issues must be developer-ready: Jules should know what to build/change without deciding the roadmap.
- For modules/solutions, require README and Mermaid service-level diagram when applicable.
- Use the default Jules environment unless the issue proves a different runtime is required.
- When code exists or is added, require focused validation commands in the issue.

## Agent role guidance

Bad:

```md
You are the customer-facing portal reference agent for Azure Reference Kit.
```

Good:

```md
You are a senior React/TypeScript, Azure Static Web Apps, and API contract developer for Azure Reference Kit.
```

Use stack-specific personas:

```text
senior Azure AI Foundry engineer and Python developer
senior Python/MCP developer and Azure integration engineer
senior Python/Azure Functions developer
senior Python/Azure Durable Functions developer
senior React/TypeScript and Azure Static Web Apps developer
senior Python/FastAPI, Docker/container, and Azure hosting developer
senior Azure identity/security engineer
senior Azure network/security engineer
senior GitHub Actions/Azure Pipelines platform engineer
senior Terraform/OpenTofu and Azure Developer CLI engineer
```

## Default validation guidance

Use the smallest meaningful validation for the changed module.

For documentation-only issues:

```text
- Markdown/manual validation of changed README/docs.
- Mermaid fence validation by inspection or tool if available.
- YAML/JSON syntax validation or manual syntax check when touching `module.yaml`, `solution.yaml`, or schemas.
```

For Python code-bearing issues, include these commands or a focused equivalent:

```bash
python --version
ruff check <changed-python-paths>
ruff format --check <changed-python-paths>
pytest <focused-test-path-or-module>
```

If there are no tests yet for a new Python module, require the smallest meaningful test. If external Azure resources are required and unavailable, require at least one local import, schema, dry-run, or deterministic unit test and document the limitation in the PR body.

For TypeScript/React code-bearing issues, include the available package-local commands, for example:

```bash
npm run lint -- --scope-or-path-if-supported
npm run typecheck
npm test -- --runInBand <focused-test-if-supported>
npm run build
```

Use only commands that exist for the package/module. If no package exists yet, do not invent a repo-wide JavaScript toolchain.

## Required issue template

```md
# [ROADMAP-ID] Outcome-oriented title

## Agent role

You are a senior <stack/domain> developer/engineer for Azure Reference Kit.

Deliver one bounded <module/solution/docs/contract> item: <exact deliverable>. The output must be developer-ready: <README/module.yaml/solution.yaml/code/tests/Mermaid/docs/proof as applicable>.

## Required behavior

- Read `AGENTS.md`, `README.md`, `docs/roadmap.md`, `docs/microsoft-reference-map.md`, and `docs/readme-standard.md` if present.
- Implement only this roadmap item: <Track X, item Y — exact item name>.
- Treat this as an implementation task, not a request for analysis, planning, or roadmap definition.
- Use current Microsoft Learn docs, not model cutoff knowledge.
- Use the default Jules environment unless a current dependency/runtime requirement proves otherwise.
- Avoid unrelated refactors and formatting churn.
- Continue until every P0 criterion passes; do not choose an arbitrary subset or silently defer in-scope work.
- Add or update meaningful tests when behavior/code changes. Do not weaken, delete, skip, or broadly mock tests to obtain green results.
- Stop only for a proven blocker requiring an unstated product, security, data, runtime, or destructive-migration decision. Report exact evidence and options.

## Documentation and references to consult

- <exact Microsoft Learn URL>
- <exact Microsoft Learn URL>
- <official SDK/docs URL if applicable>
- <public Microsoft/Azure sample repo URL if applicable>
- <other public reference repo URL if explicitly useful>

## Repository sources

- `docs/roadmap.md`
- `docs/microsoft-reference-map.md`
- `<relevant existing module/solution/doc>`
- `<relevant template>`
- `<relevant shared contract or tests>`

## Outcome

When this PR is merged, <observable repository state or behavior becomes true>.

## P0 acceptance criteria

- <exact file/folder created or updated>
- <exact behavior/contract implemented or documented>
- <README includes required sections and Mermaid diagram when applicable>
- <schemas/tests/static validation updated when applicable>
- <security/customer-safe/status/identity/runtime invariant preserved>
- <Microsoft docs URLs consulted and recorded in PR body>

## Boundaries

- Do not change <unrelated module/solution/runtime>.
- Do not implement <future roadmap item>.
- Do not create broad scaffolding, empty folder trees, or production-grade infra.
- Do not commit secrets, tokens, connection strings, `.env`, local settings, or real customer/org identifiers.
- Do not assume preview behavior is GA; document current status if relevant.

## Required proof

- Markdown/manual validation of README and Mermaid fence.
- YAML/JSON validation or manual syntax check for `module.yaml`, `solution.yaml`, or schemas.
- If Python code exists or is added:
  - `python --version`
  - `ruff check <changed-python-paths>`
  - `ruff format --check <changed-python-paths>`
  - `pytest <focused-test-path-or-module>`
- If TypeScript/React code exists or is added: package-local lint/typecheck/test/build commands that actually exist.
- If no focused test can run because external Azure resources are required, provide a local import/schema/dry-run validation and explain the limitation.
- PR body: summary, P0 mapping, docs consulted, exact commands/results, risks, and genuine follow-ups.

## Complexity / minimalism notes required in PR body

```text
Complexity / minimalism notes:
- Reused existing pattern: yes/no
- New abstraction added: yes/no, why
- Complexity risk: low/medium/high
- Follow-up needed: yes/no
```
```

## Issue sizing

Target size:

```text
focused doc/contract issue: 40-80 lines
code-bearing module issue: 60-120 lines
solution issue: 70-140 lines
```

Detailed requirements should live in repository docs such as `docs/roadmap.md`, `docs/microsoft-reference-map.md`, module READMEs, contracts, and templates. The issue should still be complete enough for Jules to execute without hidden context.

## Queue / parallelism notes

- Apply `jules` only when the issue is ready to execute.
- Multiple active `jules` issues are allowed only when independent.
- Do not label issues that touch the same folder, same module, same solution, same shared contract, or same runtime convention.
- Dependent issues should name their dependency and must not be labeled before the dependency is stable.
