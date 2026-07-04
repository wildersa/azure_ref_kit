# Deployment/IaC decision:
# This module represents a security policy and data boundary contract.
# It does not own standalone Azure resources directly.
# Instead, it provides the policy definitions that other modules (Portals, APIs, Pipelines)
# must implement when provisioning their own resources (e.g., Application Insights, Storage, Functions).

locals {
  boundary_policy = {
    name = "customer-safe-status-boundary"
    allowed_fields = [
      "business_status",
      "friendly_step_names",
      "safe_summaries",
      "safe_artifact_metadata",
      "cost_estimate",
      "timestamps",
      "correlation_ids"
    ]
    forbidden_fields = [
      "raw_logs",
      "prompts",
      "model_tool_payloads",
      "secrets",
      "stack_traces",
      "internal_resource_ids",
      "provider_payloads"
    ]
    enforcement_points = [
      "Portal API",
      "MCP Redaction Layer",
      "Foundry Agent Tools"
    ]
  }
}
