import yaml
from pathlib import Path

MODULE_ROOT = Path(__file__).parent.parent


def test_module_yaml_structure():
    """Verify that module.yaml contains required fields for the contract."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    assert config["name"] == "final-result-publisher"
    assert "inputs" in config
    assert "outputs" in config
    assert "contracts" in config
    assert "security_boundary" in config
    assert "customer_safe_boundary" in config

    # Verify contracts reference shared schemas
    assert "reads" in config["contracts"]
    assert "emits" in config["contracts"]
    assert any("pipeline-run.schema.json" in c for c in config["contracts"]["reads"])
    assert any("artifact.schema.json" in c for c in config["contracts"]["emits"])


def test_security_boundary_invariants():
    """Verify security boundary configuration in module.yaml."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    boundary = config.get("security_boundary", {})
    assert boundary.get("forbid_wildcards") is True
    assert boundary.get("forbid_secrets") is True

    roles = [r["role"] for r in boundary.get("required_roles", [])]
    assert "Storage Blob Data Contributor" in roles


def test_customer_safe_boundary_invariants():
    """Verify customer-safe boundary configuration in module.yaml."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    forbidden = config.get("customer_safe_boundary", {}).get("forbid", [])
    assert "Storage SAS URLs or connection strings" in forbidden
    assert any("Technical stack traces" in f for f in forbidden)
    assert any("Raw OCR provider payloads" in f for f in forbidden)


def test_readme_compliance():
    """Verify that README.md contains required sections and diagrams."""
    readme_path = MODULE_ROOT / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## Service-Level Diagram" in content
    assert "```mermaid" in content
    assert "## Customer-Safe Boundary" in content
    assert "### Forbidden Data (Internal-Only)" in content
    assert "- **Prompts**:" in content
    assert "- **Internal Azure IDs**:" in content
    assert "- **Correlation Preservation**:" in content
    assert "- **Internal ID Redaction**:" in content
    assert "## Failure Model" in content
    assert "## Deployment Assumptions" in content
    assert "## Known Limits" in content
