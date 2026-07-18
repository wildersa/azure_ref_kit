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

Every published opportunity must appear here as one concise row. The full problem evidence, architecture, gains, risks, and fit rationale remain in the linked document.

| ID | Opportunity | Segment | Short description | Fit | Complexity | Status |
| --- | --- | --- | --- | ---: | --- | --- |
| CROSS-001 | [Cross-system offboarding control plane](segments/cross-industry/CROSS-001-offboarding-control-plane.md) | cross-industry | Organizations with fragmented offboarding can coordinate HR events, account revocation, asset return, physical access, evidence, and overdue exceptions through one auditable control plane. | 87 | medium | researched |

The short description must use one concrete sentence, limited to roughly 40 words, explaining the problem and the proposed solution. It must not become a second copy of the full opportunity document.

## Operating links

- [Operating model](README.md)
- [Radar configuration](radar-config.yaml)
- [Radar state](radar-state.yaml)
- [Opportunity template](opportunity-template.md)
- [Execution history](history.jsonl)

## Publication rule

A watcher run may end without creating an opportunity. Publish only when a specific problem, credible evidence, measurable outcome, macro architecture, risks, and fit breakdown are available.
