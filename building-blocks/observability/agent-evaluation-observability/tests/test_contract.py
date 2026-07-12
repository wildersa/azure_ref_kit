import os
import yaml


def test_readme_contains_p0_sections():
    """Verify README.md contains all required P0 sections."""
    readme_path = os.path.join(os.path.dirname(__file__), "../README.md")
    with open(readme_path, "r") as f:
        content = f.read()

    required_sections = [
        "## Purpose",
        "## Trace Boundary",
        "## Trace and Evaluation Checklist",
        "## Customer-Safe Logging Rules",
        "### What MAY be traced",
        "### What MUST NOT be traced/logged",
        "## Minimal Evaluation Checklist",
        "## Security and Privacy Notes",
        "## Deployment / IaC Decision",
        "```mermaid",
    ]

    for section in required_sections:
        assert section in content, (
            f"README is missing required section/element: {section}"
        )


def test_readme_contains_specific_safety_rules():
    """Verify README.md contains specific safety rules required by P0."""
    readme_path = os.path.join(os.path.dirname(__file__), "../README.md")
    with open(readme_path, "r") as f:
        content = f.read()

    # Evaluation Checklist items
    checklist_items = [
        "quality",
        "safety",
        "tool-boundary",
        "answer format",
        "failure quality",
    ]
    for item in checklist_items:
        assert item in content.lower(), (
            f"README Evaluation Checklist is missing: {item}"
        )

    # Trace Checklist items
    trace_items = [
        "request id",
        "agent id/name",
        "tool name",
        "tool outcome",
        "latency",
        "status/result",
        "safety outcome",
        "sanitized summary",
    ]
    for item in trace_items:
        assert item in content.lower(), f"README Trace Checklist is missing: {item}"

    # Forbidden fields
    forbidden_fields = [
        "prompts with secrets",
        "raw tool/provider payloads",
        "raw azure devops logs",
        "tokens",
        "secrets",
        "connection strings",
        "tenant",
        "subscription",
        "customer",
        "org",
        "secret variables",
        "stack traces",
        "unrestricted user content",
    ]
    for field in forbidden_fields:
        assert field in content.lower(), (
            f"README 'What MUST NOT be traced' list is missing: {field}"
        )


def test_module_yaml_valid_and_complete():
    """Verify module.yaml is valid YAML and contains required P0 metadata."""
    yaml_path = os.path.join(os.path.dirname(__file__), "../module.yaml")
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    assert data["name"] == "agent-evaluation-observability"
    assert "inputs" in data
    assert "outputs" in data
    assert "dependencies" in data
    assert "status" in data


def test_trace_event_schema_exists_and_valid():
    """Verify trace-event.schema.json exists and is valid JSON."""
    schema_path = os.path.join(os.path.dirname(__file__), "../trace-event.schema.json")
    import json

    assert os.path.exists(schema_path)
    with open(schema_path, "r") as f:
        data = json.load(f)

    assert data["title"] == "Safe Trace Event"
    assert "properties" in data
    assert "required" in data
