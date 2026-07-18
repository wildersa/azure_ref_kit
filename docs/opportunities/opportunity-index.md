# Solution Opportunity Radar

This dashboard summarizes opportunities recorded in `opportunity-index.yaml`.

## Current state

| Metric | Value |
| --- | ---: |
| Opportunities | 1 |
| Segments configured | 18 |
| Completed research cycles | 0 |
| Current segment | `human-resources` |

## Opportunity index

Every published opportunity must appear here as one concise row. The full problem evidence, intelligent-capability design, architecture, gains, risks, and fit rationale remain in the linked document.

| ID | Opportunity | Segment | Short description | Intelligent capability | Fit | Complexity | Status |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| CROSS-001 | [AI-assisted cross-system offboarding risk control plane](segments/cross-industry/CROSS-001-offboarding-control-plane.md) | cross-industry | Organizations with fragmented offboarding can orchestrate known revocations and use access-graph anomaly detection to identify likely residual accounts, privileges, assets, and missing controls for human review. | Identity and access graph anomaly detection with risk-ranked reconciliation | 89 | large | researched |

The short description must use one concrete sentence, limited to roughly 40 words, explaining the problem, proposed solution, and material intelligent capability. It must not become a second copy of the full opportunity document.

Every opportunity must declare `AI dependency` as `supporting` or `core`. Opportunities with no material intelligent capability are invalid for this radar.

## Operating links

- [Operating model](README.md)
- [Watcher contract](watcher-contract.md)
- [Radar configuration](radar-config.yaml)
- [Radar state](radar-state.yaml)
- [Opportunity template](opportunity-template.md)
- [Execution history](history.jsonl)

## Publication rule

A watcher run may end without creating an opportunity. Publish only when a specific problem, credible evidence, a necessary intelligent capability, measurable business and model outcomes, macro architecture, risks, and fit breakdown are available.
