import yaml
from pathlib import Path
import json

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
MODULE_DIR = REPO_ROOT / "building-blocks" / "functions" / "blob-trigger-start-pipeline"


def test_module_yaml_exists():
    module_yaml = MODULE_DIR / "module.yaml"
    assert module_yaml.exists()


def test_module_yaml_structure():
    module_yaml = MODULE_DIR / "module.yaml"
    with open(module_yaml, "r") as f:
        config = yaml.safe_load(f)

    assert config["name"] == "blob-trigger-start-pipeline"
    assert "inputs" in config
    assert "outputs" in config
    assert "contracts" in config
    assert "customer_safe_boundary" in config


def test_contracts_exist():
    module_yaml = MODULE_DIR / "module.yaml"
    with open(module_yaml, "r") as f:
        config = yaml.safe_load(f)

    for contract in config.get("contracts", {}).get("emits", []):
        contract_path = REPO_ROOT / contract
        assert contract_path.exists(), f"Contract {contract} does not exist"


def test_readme_has_required_sections():
    readme = MODULE_DIR / "README.md"
    with open(readme, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## Trigger Model" in content
    assert "## Process Flow" in content
    assert "```mermaid" in content
    assert "## Customer-Safe Status Boundary" in content
    assert "## Local Validation" in content


def test_safety_invariants_in_module_yaml():
    module_yaml = MODULE_DIR / "module.yaml"
    with open(module_yaml, "r") as f:
        config = yaml.safe_load(f)

    boundary = config.get("customer_safe_boundary", {})
    forbids = boundary.get("forbids", [])

    # Key safety requirements
    assert "raw_storage_connection_strings" in forbids
    assert "sas_tokens" in forbids
    assert "raw_blob_urls" in forbids
    assert "internal_resource_ids" in forbids
    assert "prompts" in forbids
    assert "provider_payloads" in forbids


def test_pipeline_run_schema_link():
    module_yaml = MODULE_DIR / "module.yaml"
    with open(module_yaml, "r") as f:
        config = yaml.safe_load(f)

    emits = config.get("contracts", {}).get("emits", [])
    assert "shared/contracts/pipeline-run.schema.json" in emits
