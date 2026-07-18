# Opportunity segment folders

Create one folder per segment only after the first opportunity for that segment exists.

```text
docs/opportunities/segments/<segment-id>/<OPP-ID>-<short-slug>.md
```

Examples:

```text
docs/opportunities/segments/human-resources/HR-001-policy-and-procedure-assistant.md
docs/opportunities/segments/manufacturing/MFG-001-quality-deviation-investigation.md
docs/opportunities/segments/technology-software/TECH-001-log-operations-reinforcement-learning.md
```

Rules:

- use the segment IDs from `../radar-config.yaml`;
- copy `../opportunity-template.md`;
- keep one opportunity per file;
- use stable IDs even if the title changes;
- add the structured summary to `../opportunity-index.yaml`;
- record normalized `problem_keys` and `capability_keys`;
- link related opportunities instead of duplicating the same problem;
- do not create empty segment folders;
- archive nothing by deletion: use `rejected`, `superseded`, or `parked` with a reason.
