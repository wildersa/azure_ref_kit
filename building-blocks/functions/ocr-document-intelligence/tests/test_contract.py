import yaml
from pathlib import Path

MODULE_ROOT = Path(__file__).parent.parent


def test_module_yaml_structure():
    """Verify that module.yaml contains required fields for the contract."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    assert config["name"] == "ocr-document-intelligence"
    assert "inputs" in config
    assert "outputs" in config
    assert "contracts" in config
    assert "security_boundary" in config
    assert "customer_safe_boundary" in config

    # Verify contracts reference shared schemas
    assert "reads" in config["contracts"]
    assert "emits" in config["contracts"]
    assert any("artifact.schema.json" in c for c in config["contracts"]["reads"])
    assert any("pipeline-step.schema.json" in c for c in config["contracts"]["emits"])


def test_security_boundary_invariants():
    """Verify security boundary configuration in module.yaml."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    boundary = config.get("security_boundary", {})
    assert boundary.get("forbid_wildcards") is True
    assert boundary.get("forbid_secrets") is True

    roles = [r["role"] for r in boundary.get("required_roles", [])]
    assert "Cognitive Services User" in roles
    assert "Storage Blob Data Reader" in roles


def test_customer_safe_boundary_invariants():
    """Verify customer-safe boundary configuration in module.yaml."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    forbidden = config.get("customer_safe_boundary", {}).get("forbid", [])
    assert "Raw Document Intelligence JSON responses" in forbidden
    assert "Storage SAS URLs" in forbidden


def test_readme_compliance():
    """Verify that README.md contains required sections and diagrams."""
    readme_path = MODULE_ROOT / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## Service-Level Diagram" in content
    assert "```mermaid" in content
    assert "## Customer-Safe Boundary" in content
    assert "## Failure Model" in content
    assert "## Deployment Assumptions" in content
