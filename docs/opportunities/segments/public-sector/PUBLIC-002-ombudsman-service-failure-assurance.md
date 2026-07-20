# PUBLIC-002 AI-assisted ombudsman triage and service-failure assurance

## Classification

- **Segment:** public-sector
- **Primary market / jurisdiction:** Brazil
- **Status:** rejected
- **Decision date:** 2026-07-20
- **Rejection reason:** core solution overlap with an existing Brazilian public platform
- **Former fit score:** 88/100

## Decision

This opportunity is removed from the active radar.

The original brief proposed Portuguese-language classification of ombudsman manifestations, routing support, priority and deadline-risk triage, related-case analysis, and internal review workflows around Fala.BR.

Current official evidence shows that this was not researched deeply enough as an existing-solution landscape:

- Fala.BR began using artificial intelligence on 6 April 2026 to identify the manifestation type from the citizen's written report.
- The official roadmap includes automatic suggestions for subject, destination body, and public service.
- The Fala.BR treatment module already supports triage, priority, tags, responsible users, transfers, batch actions, deadline monitoring, reports, exports, and API integration.
- The Fala.BR API already exposes the AI-suggested manifestation type.

The proposed core actor, process, and outcome therefore overlap materially with the current national platform. Semantic clustering and recurrent-service-failure analysis might still be useful extensions, but the original document did not prove a sufficiently specific uncovered gap, target institution, or outcome to justify a separate solution opportunity.

## Existing solution evidence

- [Fala.BR gains AI-assisted classification](https://www.gov.br/secom/pt-br/acompanhe-a-secom/noticias/2026/04/fala-br-ganha-novo-formato-e-passa-a-usar-inteligencia-artificial-para-simplificar-atendimento-ao-cidadao) — published 2026-04-02; AI type classification launched for 2026-04-06, with subject, body, and service suggestions announced as upcoming capabilities.
- [Fala.BR Ombudsman Module manual](https://wiki.cgu.gov.br/index.php?title=Fala.BR_-_M%C3%B3dulo_Ouvidoria) — current official documentation of triage, priority, treatment, deadline monitoring, reports, AI assistance, and API integration.
- [Fala.BR API documentation](https://falabr.cgu.gov.br/help) — current API exposes `TipoSugeridoFalaBrIA` and supports external system integration.

## Lesson for the radar

Problem evidence is insufficient when a current platform already addresses the same process. Future rounds must search existing official platforms, commercial products, open-source systems, current roadmaps, and announced releases before scoring novelty or strategic differentiation.

An opportunity that overlaps an existing solution may be published only when it clearly identifies one of the following:

- a material capability gap not already covered;
- an underserved actor, jurisdiction, or operating context;
- an integration or extension with a distinct measurable outcome;
- a materially different intelligent mechanism whose value is not already delivered.

Otherwise the correct result is `no-new-fit` or `duplicate-existing-solution`.

## Final decision

- **Decision:** reject and remove from the active opportunity indexes.
- **Reason:** insufficient differentiation from the current Fala.BR platform and roadmap.
- **Implementation approval:** none.