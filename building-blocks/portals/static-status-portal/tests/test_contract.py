import yaml
from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
MODULE_DIR = Path(__file__).parent.parent


def test_module_yaml_syntax():
    """Validate that module.yaml is valid YAML and has required fields."""
    yaml_path = MODULE_DIR / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    assert config["name"] == "static-status-portal"
    assert config["type"] == "portal"
    assert "contracts" in config
    assert "reads" in config["contracts"]
    assert "security_boundary" in config
    assert config["security_boundary"]["forbid_wildcards"] is True
    assert config["security_boundary"]["forbid_secrets"] is True
    assert "customer_safe_boundary" in config
    assert "forbid" in config["customer_safe_boundary"]


def test_readme_structure():
    """Validate that README.md contains required sections and Mermaid diagram."""
    readme_path = MODULE_DIR / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    required_sections = [
        "## Purpose",
        "## Portal Responsibilities",
        "## Architecture Boundary",
        "```mermaid",
        "## UI Surface Contract",
        "### 1. Run List",
        "### 2. Run Detail & Timeline",
        "### 3. Artifacts List",
        "### 4. Cost Summary",
        "### 5. Friendly Error Panel",
        "### 6. Start Run Placeholder",
        "## API Contract Usage",
        "## Customer-Safe Status Boundary",
        "### Forbidden Data (Internal-Only)",
    ]
    for section in required_sections:
        assert section in content, (
            f"README missing required section or element: {section}"
        )


def test_mermaid_flow():
    """Ensure the Mermaid diagram contains the required flow components."""
    readme_path = MODULE_DIR / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    # Simple check for flow components in Mermaid
    assert "Customer" in content
    assert "Static Web Apps Portal" in content
    assert "Controlled Functions API" in content


def test_customer_safe_boundary_no_leaks():
    """Ensure the README explicitly forbids dangerous technical leaks."""
    readme_path = MODULE_DIR / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    forbidden_terms = [
        "Raw Logs",
        "Prompts",
        "Provider Payloads",
        "Azure Resource IDs",
        "Tenant IDs",
        "Subscription IDs",
        "Secrets",
        "Internal Exceptions",
        "SAS tokens",
        "storage keys",
        "connection strings",
        "stack traces",
        "storage_ref",
    ]
    for term in forbidden_terms:
        # Use case-insensitive search for some terms to be flexible but firm
        assert re.search(re.escape(term), content, re.IGNORECASE), (
            f"README missing explicit mention of forbidden term: {term}"
        )


def test_no_sensitive_terms_in_ui_contract():
    """Ensure that sensitive terms are NOT present in the UI Surface Contract sections as allowed fields or behavior."""
    readme_path = MODULE_DIR / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    # Extract the UI Surface Contract section
    ui_section_match = re.search(
        r"## UI Surface Contract(.*?)(?=## API Contract Usage)", content, re.DOTALL
    )
    assert ui_section_match, "Could not find UI Surface Contract section in README"
    ui_section = ui_section_match.group(1)

    # These terms should NOT be used in the UI Surface Contract as something to display or use
    # We allow them only if they are explicitly prefixed with "must never", "forbidden", "internal-only", etc.
    sensitive_terms = ["storage_ref", "SAS", "connection string", "account key"]

    for term in sensitive_terms:
        if term in ui_section:
            lines = ui_section.split("\n")
            for line in lines:
                if term in line:
                    assert any(
                        keyword in line.lower()
                        for keyword in [
                            "constraint",
                            "must never",
                            "internal-only",
                            "forbidden",
                        ]
                    ), (
                        f"Sensitive term '{term}' found in UI Surface Contract without clear restriction: {line}"
                    )


def test_contract_references_exist():
    """Validate that all contracts referenced in module.yaml exist on disk."""
    yaml_path = MODULE_DIR / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    contracts = config.get("contracts", {})
    all_refs = contracts.get("reads", [])

    for ref in all_refs:
        contract_path = REPO_ROOT / ref
        assert contract_path.exists(), f"Referenced contract does not exist: {ref}"


def test_terraform_alignment():
    """Ensure module.yaml inputs and outputs align with Terraform variables and outputs."""
    yaml_path = MODULE_DIR / "module.yaml"
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)

    # Load Terraform variables
    variables_path = MODULE_DIR / "infra/terraform/variables.tf"
    with open(variables_path, "r") as f:
        variables_content = f.read()

    # Load Terraform outputs
    outputs_path = MODULE_DIR / "infra/terraform/outputs.tf"
    with open(outputs_path, "r") as f:
        outputs_content = f.read()

    # Check inputs
    yaml_inputs = [i["name"] for i in config.get("inputs", [])]
    for var_name in re.findall(r'variable\s+"([^"]+)"', variables_content):
        assert var_name in yaml_inputs, f"Terraform variable '{var_name}' missing from module.yaml inputs"

    # Check outputs
    yaml_outputs = [o["name"] for o in config.get("outputs", [])]
    for out_name in re.findall(r'output\s+"([^"]+)"', outputs_content):
        assert out_name in yaml_outputs, f"Terraform output '{out_name}' missing from module.yaml outputs"
