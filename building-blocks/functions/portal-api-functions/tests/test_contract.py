import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
MODULE_DIR = Path(__file__).parent.parent


def test_module_yaml_syntax():
    """Validate that module.yaml is valid YAML and has required fields."""
    yaml_path = MODULE_DIR / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    assert config["name"] == "portal-api-functions"
    assert "contracts" in config
    assert "reads" in config["contracts"]
    assert "emits" in config["contracts"]
    assert "security_boundary" in config
    assert config["security_boundary"]["forbid_wildcards"] is True
    assert config["security_boundary"]["forbid_secrets"] is True


def test_readme_structure():
    """Validate that README.md contains required sections and Mermaid diagram."""
    readme_path = MODULE_DIR / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## Architecture Boundary" in content
    assert "```mermaid" in content
    assert "## API Contract" in content
    assert "## Customer-Safe Boundary" in content
    assert "### Allowed Customer-Facing Data" in content
    assert "### Forbidden Data (Internal-Only)" in content


def test_customer_safe_boundary_no_leaks():
    """Ensure the README explicitly forbids dangerous technical leaks."""
    readme_path = MODULE_DIR / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    forbidden_terms = [
        "Raw Logs",
        "Prompts",
        "Secrets",
        "Technical IDs",
        "Provider Payloads",
    ]
    for term in forbidden_terms:
        assert term in content, (
            f"README missing explicit mention of forbidden term: {term}"
        )


def test_contract_references_exist():
    """Validate that all contracts referenced in module.yaml exist on disk."""
    yaml_path = MODULE_DIR / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    contracts = config.get("contracts", {})
    all_refs = contracts.get("reads", []) + contracts.get("emits", [])

    for ref in all_refs:
        contract_path = REPO_ROOT / ref
        assert contract_path.exists(), f"Referenced contract does not exist: {ref}"
