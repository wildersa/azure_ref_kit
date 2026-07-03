# Pipeline Assistant Foundry

Azure AI Foundry agent reference for customer questions about a pipeline execution.

## Purpose

Let a customer ask questions such as:

- What happened in this run?
- Why did it fail?
- What do I need to fix?
- Which document was generated?
- How much did this run cost?

## Tool boundary

The agent should use safe tools over curated business data:

- get pipeline status;
- get pipeline steps;
- explain friendly error;
- get artifacts;
- estimate cost;
- request human review.

It should not read raw logs, secrets, prompts, keys, or unrestricted Azure resources.
