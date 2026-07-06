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
        "## Customer-Safe Logging Rules",
        "### What MAY be traced",
        "### What MUST NOT be traced/logged",
        "## Minimal Evaluation Checklist",
        "## Monitoring Signals",
        "## Known Limits",
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

    # Checklist items
    checklist_items = ["groundedness", "tool-use", "safety", "no-leak"]
    for item in checklist_items:
        assert item in content.lower(), (
            f"README Evaluation Checklist is missing: {item}"
        )

    # Forbidden fields
    forbidden_fields = [
        "prompts",
        "stack traces",
        "secrets",
        "tokens",
        "provider payloads",
        "storage paths",
        "subscription ids",
        "tenant ids",
        "resource ids",
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
