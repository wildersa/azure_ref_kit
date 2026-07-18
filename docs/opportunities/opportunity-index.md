# Solution Opportunity Radar

This dashboard summarizes opportunities recorded in `opportunity-index.yaml`.

## Current state

| Metric | Value |
| --- | ---: |
| Opportunities | 4 |
| Segments configured | 18 |
| Completed research cycles | 0 |
| Current segment | `retail-ecommerce` |
| Default primary market | `Brazil` |

## Opportunity index

Every published opportunity must appear here as one concise row. The full problem evidence, intelligent-capability design, architecture, gains, risks, and fit rationale remain in the linked document.

| ID | Opportunity | Segment | Short description | Intelligent capability | Fit | Complexity | Status |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| CROSS-001 | [AI-assisted cross-system offboarding risk control plane](segments/cross-industry/CROSS-001-offboarding-control-plane.md) | cross-industry | Organizations with fragmented offboarding can orchestrate known revocations and use access-graph anomaly detection to identify likely residual accounts, privileges, assets, and missing controls for human review. | Identity and access graph anomaly detection with risk-ranked reconciliation | 89 | large | researched |
| HR-001 | [AI skills-evidence graph for internal mobility and reskilling](segments/human-resources/HR-001-skills-evidence-mobility-graph.md) | human-resources | Organizations can convert employee-approved work evidence into a governed skills graph that identifies capability gaps, ranks internal transition paths, and recommends targeted reskilling without making autonomous employment decisions. | Evidence-grounded skill extraction, taxonomy mapping, gap inference, and internal transition-path ranking | 89 | large | researched |
| FIN-001 | [Real-time Pix scam and mule-account intervention with MED intelligence](segments/financial-services/FIN-001-app-scam-intervention.md) | financial-services | Brazilian Pix participants can combine Banco Central security signals, transaction behavior, device context, and payment graphs to detect scams and contas laranja, apply proportionate controls, and prioritize MED investigation before funds disperse. | Calibrated Pix scam-risk prediction and graph-based conta-laranja and fund-dispersion detection | 92 | large | researched |
| HEALTH-001 | [AI-assisted SUS specialist-access and queue orchestration](segments/healthcare/HEALTH-001-sus-specialist-access-orchestration.md) | healthcare | Brazilian SUS regulation centers can combine protocol rules with demand, capacity, geography, wait-time, cancellation, and clinical-context models to recommend equitable specialist-access queues and recover unused appointment capacity under human control. | Constrained demand-capacity forecasting, no-show prediction, and protocol-aware queue and slot recommendation | 88 | large | researched |

The short description must use one concrete sentence, limited to roughly 40 words, explaining the problem, proposed solution, and material intelligent capability. It must not become a second copy of the full opportunity document.

Every opportunity must declare `AI dependency` as `supporting` or `core`. Opportunities with no material intelligent capability are invalid for this radar.

The default target market is Brazil. New opportunities require current Brazilian problem evidence and current Brazilian regulatory context when regulated. Foreign sources may support comparison or architecture but cannot be the main proof of applicability.

## Operating links

- [Operating model](README.md)
- [Watcher contract](watcher-contract.md)
- [Radar configuration](radar-config.yaml)
- [Radar state](radar-state.yaml)
- [Opportunity template](opportunity-template.md)
- [Execution history](history.jsonl)

## Publication rule

A watcher run may end without creating an opportunity. Publish only when a specific problem, current Brazilian evidence, a necessary intelligent capability, measurable business and model outcomes, macro architecture, risks, and fit breakdown are available.
