# OCR Document Intelligence

Reference OCR/extraction function using Azure AI Document Intelligence.

## Purpose

Extract text, fields, confidence values, and artifacts from documents as one step in a larger pipeline.

## Inputs

- document artifact reference;
- document type or classifier hint;
- pipeline run id;
- customer/tenant context.

## Outputs

- extracted text;
- structured fields;
- confidence summary;
- generated artifacts;
- step status.

## Rule

Return normalized pipeline output. Do not force callers to understand raw provider payloads.
