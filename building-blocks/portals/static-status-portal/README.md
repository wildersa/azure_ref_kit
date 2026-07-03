# Static Status Portal

Customer-facing portal reference for tracking pipeline executions.

## Purpose

Expose business-friendly status for AI pipelines without requiring the customer to access Azure Portal, Functions logs, Foundry, or technical dashboards.

## Expected features

- list pipeline runs;
- view current status and progress;
- view pipeline steps;
- display friendly errors;
- show generated artifacts;
- show estimated cost when available;
- open a pipeline assistant/chat when enabled.

## Azure fit

Default host: Azure Static Web Apps.

The portal should call a backend API instead of reading Azure resources directly.
