# Solution Opportunity Radar

This dashboard summarizes opportunities recorded in `opportunity-index.yaml`.

## Current state

| Metric | Value |
| --- | ---: |
| Opportunities | 8 |
| Segments configured | 18 |
| Completed research cycles | 0 |
| Current segment | `public-sector` |
| Default primary market | `Brazil` |

## Opportunity index

Every published opportunity must appear here as one concise row. The full problem evidence, intelligent-capability design, architecture, gains, risks, and fit rationale remain in the linked document.

| ID | Opportunity | Segment | Short description | Intelligent capability | Fit | Complexity | Status |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| CROSS-001 | [AI-assisted cross-system offboarding risk control plane](segments/cross-industry/CROSS-001-offboarding-control-plane.md) | cross-industry | Organizations with fragmented offboarding can orchestrate known revocations and use access-graph anomaly detection to identify likely residual accounts, privileges, assets, and missing controls for human review. | Identity and access graph anomaly detection with risk-ranked reconciliation | 89 | large | researched |
| HR-001 | [AI skills-evidence graph for internal mobility and reskilling](segments/human-resources/HR-001-skills-evidence-mobility-graph.md) | human-resources | Organizations can convert employee-approved work evidence into a governed skills graph that identifies capability gaps, ranks internal transition paths, and recommends targeted reskilling without making autonomous employment decisions. | Evidence-grounded skill extraction, taxonomy mapping, gap inference, and internal transition-path ranking | 89 | large | researched |
| FIN-001 | [Real-time Pix scam and mule-account intervention with MED intelligence](segments/financial-services/FIN-001-app-scam-intervention.md) | financial-services | Brazilian Pix participants can combine Banco Central security signals, transaction behavior, device context, and payment graphs to detect scams and contas laranja, apply proportionate controls, and prioritize MED investigation before funds disperse. | Calibrated Pix scam-risk prediction and graph-based conta-laranja and fund-dispersion detection | 92 | large | researched |
| HEALTH-001 | [AI-assisted SUS specialist-access and queue orchestration](segments/healthcare/HEALTH-001-sus-specialist-access-orchestration.md) | healthcare | Brazilian SUS regulation centers can combine protocol rules with demand, capacity, geography, wait-time, cancellation, and clinical-context models to recommend equitable specialist-access queues and recover unused appointment capacity under human control. | Constrained demand-capacity forecasting, no-show prediction, and protocol-aware queue and slot recommendation | 88 | large | researched |
| RETAIL-001 | [AI-assisted shelf-availability and retail-loss orchestration](segments/retail-ecommerce/RETAIL-001-shelf-availability-loss-orchestration.md) | retail-ecommerce | Brazilian retailers can combine shelf images, inventory, sales, replenishment, and loss events to detect operational rupture and shrinkage anomalies, rank corrective store tasks, and verify execution under human control. | Multimodal shelf-state recognition with inventory-loss anomaly detection and intervention ranking | 89 | large | researched |
| ENERGY-001 | [AI-assisted water-leak detection and field verification](segments/energy-utilities/ENERGY-001-ai-assisted-water-leak-detection.md) | energy-utilities | Brazilian water utilities can use acoustic and hydraulic anomaly models to rank suspected hidden leaks, direct field verification, and measure recovered water while retaining geophone confirmation and cost-benefit controls. | Acoustic leak classification and hydraulic anomaly ranking with human-confirmed localization | 87 | medium | researched |
| TELCO-001 | [AI-assisted network incident correlation and dispatch triage](segments/telecommunications/TELCO-001-ai-assisted-network-incident-correlation.md) | telecommunications | Brazilian telecom NOCs can correlate alarms, topology, performance, tickets, and customer-impact signals to rank likely root causes, recommend safe runbooks, and avoid unnecessary field dispatches under engineer approval. | Topology-aware alarm correlation, incident clustering, root-cause ranking, and dispatch-necessity prediction | 86 | large | hypothesis |
| EDU-001 | [AI-assisted student-persistence early warning and support triage](segments/education/EDU-001-student-persistence-early-warning.md) | education | Brazilian higher-education institutions can combine academic progression, attendance, LMS activity, financial and service signals to rank dropout risk, explain contributing factors, and route bounded support actions under advisor control. | Calibrated student-persistence risk prediction, risk-factor ranking, and support-case prioritization | 83 | medium | hypothesis |

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