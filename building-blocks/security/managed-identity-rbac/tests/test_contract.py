import os
import yaml
import pathlib
from azure.identity import DefaultAzureCredential


def test_get_default_credential_helper():
    """Verify that the get_default_credential helper behaves as expected."""
    # We can't easily test the actual credential behavior without environment setup,
    # but we can verify the import and basic function presence.
    try:
        from ..src.identity import get_default_credential
        credential = get_default_credential()
        assert isinstance(credential, DefaultAzureCredential)
    except ImportError:
        # Fallback for different test execution contexts
        import sys
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from src.identity import get_default_credential
        credential = get_default_credential()
        assert isinstance(credential, DefaultAzureCredential)


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
    recommended_roles = {
        role_entry.get("role", "") for role_entry in sec_boundary.get("recommended_roles", [])
    }
    for role_name in recommended_roles:
        assert "*" not in role_name, f"Role '{role_name}' should not contain wildcards"
        assert "Owner" not in role_name, f"Role '{role_name}' should not be 'Owner'"
        assert "Contributor" not in role_name or "Data" in role_name, (
            f"Role '{role_name}' should be a Data Plane role if using Contributor"
        )

    # Verify that the Terraform implementation enforces the recommended role allowlist
    tf_variables_path = (
        pathlib.Path(__file__).parent.parent / "infra" / "terraform" / "variables.tf"
    )
    with open(tf_variables_path, "r") as f:
        tf_content = f.read()

    # The validation condition should contain the recommended roles from module.yaml
    for role in recommended_roles:
        assert f'"{role}"' in tf_content, f"Role '{role}' missing from Terraform allowlist"

    # Verify fail-closed: it should NOT contain generic permissive roles
    for forbidden in ["Owner", "Contributor", "User Access Administrator", "*"]:
        assert (
            forbidden not in tf_content or f'"{forbidden}"' not in tf_content
        ), f"Forbidden role/wildcard '{forbidden}' found in Terraform validation"


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
