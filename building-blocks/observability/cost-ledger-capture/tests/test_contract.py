import yaml
from pathlib import Path

MODULE_ROOT = Path(__file__).parent.parent


def test_module_yaml_structure():
    """Verify that module.yaml contains required fields for the cost ledger contract."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    assert config["name"] == "cost-ledger-capture"
    assert config["type"] == "observability"
    assert "inputs" in config
    assert "outputs" in config
    assert "contracts" in config
    assert "customer_safe_boundary" in config

    # Verify contracts reference shared schemas
    assert "emits" in config["contracts"]
    assert any("cost-ledger.schema.json" in c for c in config["contracts"]["emits"])


def test_customer_safe_boundary_invariants():
    """Verify customer-safe boundary configuration in module.yaml."""
    yaml_path = MODULE_ROOT / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    forbidden = config.get("customer_safe_boundary", {}).get("forbid", [])
    assert "Raw billing records" in forbidden
    assert "Azure Subscription IDs" in forbidden
    assert "Azure Tenant IDs" in forbidden
    assert "Resource Group names" in forbidden
    assert "Secrets, tokens, and connection strings" in forbidden


def test_readme_compliance():
    """Verify that README.md contains required sections and diagrams."""
    readme_path = MODULE_ROOT / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## Contract vs Authoritative Billing" in content
    assert "## Input Fields" in content
    assert "## Service-Level Diagram" in content
    assert "```mermaid" in content
    assert "## Customer-Safe Boundary" in content
    assert "### Allowed" in content
    assert "### Forbidden" in content

    # Verify Mermaid diagram contains the expected flow
    assert "Cost Ledger Capture" in content
    assert "Internal Cost Ledger" in content
    assert "Customer Portal" in content
