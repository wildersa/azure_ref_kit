import yaml
import pathlib


def test_module_yaml_structure():
    """Verify that module.yaml has the required fields and security invariants."""
    module_path = pathlib.Path(__file__).parent.parent / "module.yaml"
    assert module_path.exists(), "module.yaml should exist"

    with open(module_path, "r") as f:
        module = yaml.safe_load(f)

    # Check basic fields
    assert module["name"] == "key-vault-secret-handling"
    assert "security_boundary" in module
    assert "customer_safe_boundary" in module

    # Check security invariants
    sec_boundary = module["security_boundary"]
    assert sec_boundary.get("forbid_wildcards") is True
    assert sec_boundary.get("forbid_secrets") is True


def test_readme_sections():
    """Verify that README.md contains mandatory sections."""
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    assert readme_path.exists(), "README.md should exist"

    with open(readme_path, "r") as f:
        content = f.read()

    mandatory_sections = [
        "## Purpose",
        "## When to Use",
        "## When Not to Use",
        "## Practical Guidance",
        "## Allowed vs. Forbidden Patterns",
        "## Copyable Documentation Snippets",
        "## Deployment/IaC Decision",
        "## Known Limits",
        "```mermaid",
    ]

    for section in mandatory_sections:
        assert section in content, f"README should contain '{section}'"


def test_no_secrets_in_docs():
    """Verify no common secret patterns exist in the building block folder."""
    root_path = pathlib.Path(__file__).parent.parent
    forbidden_patterns = [
        "client_secret =",
        "password =",
        "api_key =",
        "account_key =",
    ]

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in [".md", ".yaml", ".py", ".tf"]:
            if file_path.name == "test_contract.py":
                continue
            with open(file_path, "r", errors="ignore") as f:
                content = f.read().lower()
                for pattern in forbidden_patterns:
                    assert pattern not in content, f"Found forbidden pattern '{pattern}' in {file_path}"
