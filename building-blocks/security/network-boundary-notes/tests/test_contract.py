import yaml
import pathlib


def test_module_yaml_structure():
    """Verify that module.yaml has the required fields and security invariants."""
    module_path = pathlib.Path(__file__).parent.parent / "module.yaml"
    assert module_path.exists(), "module.yaml should exist"

    with open(module_path, "r") as f:
        module = yaml.safe_load(f)

    # Check basic fields
    assert module["name"] == "network-boundary-notes"
    assert "security_boundary" in module

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
        "## Network Architecture Overview",
        "## Boundary Definitions",
        "### Customer-Facing Boundary",
        "### Internal API Boundary",
        "### Storage and Artifact Boundary",
        "### Agent and Tool Boundary",
        "### Observability and Log Boundary",
        "## Practical Guidance: When to Use",
        "## Defense in Depth",
        "## Production-Grade Infrastructure Note",
        "## References",
        "```mermaid",
    ]

    for section in mandatory_sections:
        assert section in content, f"README should contain '{section}'"


def test_no_secrets_in_docs():
    """Verify no common secret patterns exist in the building block folder."""
    root_path = pathlib.Path(__file__).parent.parent
    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in [".md", ".yaml", ".py"]:
            if file_path.name == "test_contract.py":
                continue
            with open(file_path, "r", errors="ignore") as f:
                content = f.read().lower()
                # Simple checks for potential secrets
                assert "password" not in content
                assert "client_secret" not in content
                assert "connectionstring" not in content
