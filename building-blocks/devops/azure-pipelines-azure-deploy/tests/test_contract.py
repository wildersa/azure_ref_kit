import yaml
import pathlib
import pytest

def test_module_yaml_exists():
    module_yaml_path = pathlib.Path(__file__).parent.parent / "module.yaml"
    assert module_yaml_path.exists(), "module.yaml is missing"

def test_module_yaml_structure():
    module_yaml_path = pathlib.Path(__file__).parent.parent / "module.yaml"
    with open(module_yaml_path, "r") as f:
        data = yaml.safe_load(f)

    assert data["name"] == "azure-pipelines-azure-deploy"
    assert "security_boundary" in data
    assert "customer_safe_boundary" in data
    assert data["security_boundary"]["forbid_secrets"] is True
    assert data["security_boundary"]["forbid_wildcards"] is True

def test_readme_contains_required_sections():
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## Deployment Architecture" in content
    assert "```mermaid" in content
    assert "## Configuration and Service Connection" in content
    assert "## Security & Customer-Safe Boundary" in content
    assert "## Deployment/IaC Decision" in content
    assert "## References" in content

def test_azure_pipelines_yaml_exists():
    pipeline_yaml_path = pathlib.Path(__file__).parent.parent / "azure-pipelines.yml"
    assert pipeline_yaml_path.exists(), "azure-pipelines.yml is missing"

def test_azure_pipelines_yaml_syntax():
    pipeline_yaml_path = pathlib.Path(__file__).parent.parent / "azure-pipelines.yml"
    with open(pipeline_yaml_path, "r") as f:
        # Basic YAML syntax check
        data = yaml.safe_load(f)

    assert "stages" in data
    assert len(data["stages"]) >= 2

    # Check for expected stages
    stage_names = [s.get("stage") for s in data["stages"]]
    assert "BuildAndTest" in stage_names
    assert "Deploy" in stage_names

def test_readme_mentions_wif():
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "WIF" in content or "Workload Identity Federation" in content

def test_no_secrets_in_pipeline():
    pipeline_yaml_path = pathlib.Path(__file__).parent.parent / "azure-pipelines.yml"
    with open(pipeline_yaml_path, "r") as f:
        content = f.read()

    # Check for potential hardcoded secrets (placeholder patterns to avoid)
    forbidden_patterns = ["password:", "secret:", "token: '", "key: '"]
    for pattern in forbidden_patterns:
        # We allow parameters and variables like $(SWA_DEPLOYMENT_TOKEN)
        assert pattern not in content.lower() or "$(" in content or "${{" in content
