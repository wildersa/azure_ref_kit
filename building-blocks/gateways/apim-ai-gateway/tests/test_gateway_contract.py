import os
import yaml
import xml.etree.ElementTree as ET
import pytest

# Constants
MODULE_DIR = os.path.join(os.path.dirname(__file__), "..")
MODULE_YAML = os.path.join(MODULE_DIR, "module.yaml")
POLICY_XML = os.path.join(MODULE_DIR, "infra", "terraform", "policies", "model-access.xml")
TERRAFORM_MAIN = os.path.join(MODULE_DIR, "infra", "terraform", "main.tf")

def test_module_yaml_structure():
    """Verify that module.yaml exists and has required fields."""
    assert os.path.exists(MODULE_YAML)
    with open(MODULE_YAML, 'r') as f:
        data = yaml.safe_load(f)

    assert data['name'] == 'apim-ai-gateway'
    assert 'inputs' in data
    assert 'outputs' in data
    assert 'security_boundary' in data
    assert 'customer_safe_boundary' in data

def test_policy_xml_parsing():
    """Verify that the APIM policy XML is well-formed and contains required GenAI policies."""
    assert os.path.exists(POLICY_XML)
    tree = ET.parse(POLICY_XML)
    root = tree.getroot()

    # Check for llm-token-limit
    token_limit = root.find(".//llm-token-limit")
    assert token_limit is not None, "Policy must contain <llm-token-limit>"
    assert token_limit.get('tokens-per-minute') == "{{TOKEN_LIMIT_PER_MINUTE}}"

    # Check for llm-emit-token-metric
    emit_metric = root.find(".//llm-emit-token-metric")
    assert emit_metric is not None, "Policy must contain <llm-emit-token-metric>"

    # Check for authentication-managed-identity
    auth_identity = root.find(".//authentication-managed-identity")
    assert auth_identity is not None, "Policy must contain <authentication-managed-identity>"
    assert auth_identity.get('resource') == "https://cognitiveservices.azure.com"

    # Check for header redaction (api-key should be deleted)
    set_header_api_key = root.find(".//inbound/set-header[@name='api-key'][@exists-action='delete']")
    assert set_header_api_key is not None, "Policy must redact 'api-key' in inbound"

def test_terraform_security_invariants():
    """Verify security invariants in Terraform main.tf."""
    assert os.path.exists(TERRAFORM_MAIN)
    with open(TERRAFORM_MAIN, 'r') as f:
        content = f.read()

    # Verify User-Assigned Identity is used
    assert "azurerm_user_assigned_identity" in content
    assert "identity {" in content
    assert "type         = \"UserAssigned\"" in content

    # Verify least-privilege role assignment (Cognitive Services User)
    assert "azurerm_role_assignment" in content
    assert "role_definition_name = \"Cognitive Services User\"" in content

    # Ensure no hardcoded secrets or keys are obvious (minimal check)
    assert "api-key" not in content.lower() or "set-header" in content.lower() # api-key is in policy text within main.tf
    assert "client_secret" not in content.lower()
