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

    assert data["name"] == "github-actions-azure-deploy"
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
    assert "## Configuration and Secrets" in content
    assert "## Security & Customer-Safe Boundary" in content
    assert "## Deployment/IaC Decision" in content
    assert "## References" in content

def test_readme_no_secrets():
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    # Simple check for common secret placeholders that should be avoided if they look like real secrets
    forbidden_placeholders = ["your-key", "AZURE_OPENAI_KEY"]
    for placeholder in forbidden_placeholders:
        assert placeholder not in content, f"Forbidden placeholder '{placeholder}' found in README"

def test_readme_mentions_oidc():
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "OIDC" in content or "OpenID Connect" in content
    assert "id-token: write" in content
