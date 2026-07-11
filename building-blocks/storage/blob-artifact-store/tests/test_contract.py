import os
import yaml
import re
import pytest

MODULE_ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_module_yaml_contract():
    """Verify module.yaml has all required P0 fields and correct metadata."""
    path = os.path.join(MODULE_ROOT, "module.yaml")
    assert os.path.exists(path)

    with open(path, "r") as f:
        content = yaml.safe_load(f)

    assert content["name"] == "blob-artifact-store"
    assert content["type"] == "storage"
    assert content["status"] == "implemented"

    # Check for required P0 inputs
    input_names = [i["name"] for i in content["inputs"]]
    required_inputs = [
        "ARTIFACT_STORE_BLOB_ENDPOINT",
        "ARTIFACT_CONTAINER_NAME",
        "SAS_MAX_LIFETIME_HOURS",
        "runtime_principal_id",
        "allowed_ips",
    ]
    for ri in required_inputs:
        assert ri in input_names, f"Missing required input in module.yaml: {ri}"

    # Check for required P0 deployment contract
    assert "deployment" in content
    assert "identity" in content["deployment"]
    assert "network" in content["deployment"]
    assert content["deployment"]["network"]["default_action"] == "Deny"


def test_terraform_variables_contract():
    """Verify Terraform variables.tf matches the module.yaml and P0 requirements."""
    path = os.path.join(MODULE_ROOT, "infra", "terraform", "variables.tf")
    assert os.path.exists(path)

    with open(path, "r") as f:
        content = f.read()

    # Verify P0 variable existence
    assert 'variable "runtime_principal_id"' in content
    assert 'default     = null' not in content, "runtime_principal_id must be required (no default)."
    assert 'variable "allowed_ips"' in content
    assert 'default     = []' not in content, "allowed_ips must be required (no default) to enforce explicit network path."
    assert 'length(var.allowed_ips) > 0' in content, "allowed_ips must have a validation rule for non-empty list."
    assert 'variable "container_name"' in content

    # Verify RE2 compliance (no lookahead)
    assert "(?!.*--)" not in content, "RE2 does not support lookahead. Use !strcontains instead."
    assert "strcontains" in content


def test_terraform_security_contract():
    """Verify Terraform security settings meet P0 criteria."""
    path = os.path.join(MODULE_ROOT, "infra", "terraform", "main.tf")
    assert os.path.exists(path)

    with open(path, "r") as f:
        content = f.read()

    # Verify network security
    assert 'default_action = "Deny"' in content
    assert 'public_network_access_enabled  = true' in content
    assert 'ip_rules       = var.allowed_ips' in content

    # Verify identity and access security
    assert 'shared_access_key_enabled      = false' in content
    assert 'https_only_enabled            = true' in content
    assert 'min_tls_version                = "TLS1_2"' in content

    # Verify public access disabled on container
    assert 'container_access_type = "private"' in content


def test_terraform_ip_validation_regex():
    """Verify that the IP validation regex correctly identifies valid and invalid IPs/CIDRs."""
    path = os.path.join(MODULE_ROOT, "infra", "terraform", "variables.tf")
    with open(path, "r") as f:
        content = f.read()

    # Extract the regex pattern from variables.tf specifically for allowed_ips
    # Use re.DOTALL to match across lines if necessary, and look for allowed_ips context
    match = re.search(r'variable "allowed_ips".*?regex\("([^"]+)"', content, re.DOTALL)
    assert match, "Could not find IP validation regex for allowed_ips in variables.tf"
    pattern = match.group(1).replace("\\\\", "\\")

    # Test valid cases
    valid_ips = [
        "192.168.1.1",
        "0.0.0.0",
        "255.255.255.255",
        "8.8.8.8/32",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "1.1.1.1/0",
    ]
    for ip in valid_ips:
        assert re.match(pattern, ip), f"Regex failed to match valid IP: {ip}"

    # Test invalid cases
    invalid_ips = [
        "256.256.256.256",
        "1.2.3.4.5",
        "1.2.3",
        "a.b.c.d",
        "192.168.1.1/33",
        "1.1.1.1/-1",
        "999.999.999.999",
    ]
    for ip in invalid_ips:
        assert not re.match(pattern, ip), f"Regex incorrectly matched invalid IP: {ip}"


def test_readme_standard_sections():
    """Verify README has all mandatory sections from standard."""
    path = os.path.join(MODULE_ROOT, "README.md")
    assert os.path.exists(path)

    with open(path, "r") as f:
        content = f.read()

    mandatory_sections = [
        "## Purpose",
        "## When to Use",
        "## When NOT to Use",
        "## Environment Variables",
        "## Security Boundary",
        "## Azure Hosting Notes",
        "## Known Limits",
    ]
    for section in mandatory_sections:
        assert section in content, f"README missing mandatory section: {section}"

    # Verify Mermaid diagram
    assert "```mermaid" in content
    assert "sequenceDiagram" in content


def test_terraform_no_null_resource():
    """Verify that the warning null_resource is removed in favor of a required variable."""
    path = os.path.join(MODULE_ROOT, "infra", "terraform", "main.tf")
    with open(path, "r") as f:
        content = f.read()
    assert "null_resource" not in content


def test_no_secrets_in_code():
    """Safety check: ensure no hardcoded secrets or account keys are in the codebase."""
    for root, dirs, files in os.walk(MODULE_ROOT):
        for file in files:
            if file.endswith((".py", ".tf", ".yaml", ".md")):
                path = os.path.join(root, file)
                with open(path, "r", errors="ignore") as f:
                    content = f.read().lower()
                    assert "account_key" not in content or "shared_access_key_enabled = false" in content
                    assert "connection_string" not in content or "redacted" in content or "environment variable" in content
