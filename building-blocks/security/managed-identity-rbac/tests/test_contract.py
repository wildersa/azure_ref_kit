import yaml
import pathlib


def test_module_yaml_structure():
    """Verify that module.yaml has the required fields and security invariants."""
    module_path = pathlib.Path(__file__).parent.parent / "module.yaml"
    assert module_path.exists(), "module.yaml should exist"

    with open(module_path, "r") as f:
        module = yaml.safe_load(f)

    # Check basic fields
    assert module["name"] == "managed-identity-rbac"
    assert "security_boundary" in module
    assert "customer_safe_boundary" in module

    # Verify input alignment with Terraform
    inputs = {i["name"] for i in module.get("inputs", [])}
    expected_inputs = {
        "workload_name",
        "location",
        "resource_group_name",
        "target_resource_id",
        "role_definition_name",
    }
    assert expected_inputs.issubset(inputs), f"Missing required inputs: {expected_inputs - inputs}"

    # Verify output alignment with Terraform
    outputs = {o["name"] for o in module.get("outputs", [])}
    expected_outputs = {
        "identity_principal_id",
        "identity_client_id",
        "role_assignment_id",
    }
    assert expected_outputs.issubset(
        outputs
    ), f"Missing required outputs: {expected_outputs - outputs}"

    # Check security invariants
    sec_boundary = module["security_boundary"]
    assert sec_boundary.get("forbid_wildcards") is True
    assert sec_boundary.get("forbid_secrets") is True

    # Check recommended roles for wildcards
    for role_entry in sec_boundary.get("recommended_roles", []):
        role_name = role_entry.get("role", "")
        assert "*" not in role_name, f"Role '{role_name}' should not contain wildcards"
        assert "Owner" not in role_name, f"Role '{role_name}' should not be 'Owner'"
        assert "Contributor" not in role_name or "Data" in role_name, (
            f"Role '{role_name}' should be a Data Plane role if using Contributor"
        )


def test_readme_sections():
    """Verify that README.md contains mandatory sections."""
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    assert readme_path.exists(), "README.md should exist"

    with open(readme_path, "r") as f:
        content = f.read()

    mandatory_sections = [
        "## Purpose",
        "## Scenarios",
        "## Identity Choice Guidance",
        "## RBAC Scope Guidance",
        "## Local Development Fallback",
        "## Azure Deployment Assumptions",
        "## Known Limits",
        "## Validation Notes",
        "```mermaid",
    ]

    for section in mandatory_sections:
        assert section in content, f"README should contain '{section}'"


def test_no_secrets_in_docs():
    """Verify no common secret patterns exist in the building block folder."""
    root_path = pathlib.Path(__file__).parent.parent
    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in [".md", ".yaml", ".py", ".tf"]:
            if file_path.name == "test_contract.py":
                continue
            with open(file_path, "r", errors="ignore") as f:
                content = f.read().lower()
                # Simple checks for potential secrets, excluding descriptive mentions
                if "client_secret" in content:
                    # Allow mention of AZURE_CLIENT_SECRET in the context of local dev fallback
                    assert "azure_client_secret" in content
                    assert content.count("client_secret") <= content.count(
                        "azure_client_secret"
                    )

                if "connectionstring" in content:
                    # Allow descriptive mentions
                    assert any(
                        allowed in content
                        for allowed in [
                            "reference",
                            "azurefilesconnectionstring",
                            "connection string requirement",
                        ]
                    )
