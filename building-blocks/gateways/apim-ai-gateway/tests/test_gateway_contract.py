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

    # Check for validate-jwt (explicit Entra JWT validation)
    validate_jwt = root.find(".//validate-jwt")
    assert validate_jwt is not None, "Policy must contain <validate-jwt> for authentication boundary"
    assert validate_jwt.get('header-name') == "Authorization"

    # Check for set-backend-service (explicit wiring to registered backend)
    set_backend = root.find(".//set-backend-service")
    assert set_backend is not None, "Policy must contain <set-backend-service> to wire to the backend"
    assert set_backend.get('backend-id') == "model-backend"

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
    assert auth_identity.get('client-id') == "{{CLIENT_ID}}", "Policy must explicitly set client-id for user-assigned identity"

    # Check for header redaction (api-key should be deleted)
    set_header_api_key = root.find(".//inbound/set-header[@name='api-key'][@exists-action='delete']")
    assert set_header_api_key is not None, "Policy must redact 'api-key' in inbound"

    # Check for request size protection
    choose_size = root.find(".//inbound/choose/when[@condition]")
    assert choose_size is not None
    assert "MAX_REQUEST_SIZE_BYTES" in choose_size.get('condition')
    assert root.find(".//inbound/choose/when/return-response/set-status[@code='413']") is not None

    # Check for safe trace telemetry
    trace = root.find(".//outbound/trace[@source='AI-Gateway-Safe-Trace']")
    assert trace is not None
    assert trace.find("message") is not None
    assert "context.RequestId" in trace.find("message").text
    assert "context.Elapsed.TotalMilliseconds" in trace.find("message").text

    # Forbidden: Check for sensitive logging (robust negative check)
    xml_string = ET.tostring(root, encoding='unicode')
    forbidden_terms = ["context.Request.Body", "context.Response.Body", "Authorization", "api-key"]

    # Check that forbidden terms do not appear inside trace or log policies
    # This is a bit more robust than simple string matching
    traces = root.findall(".//trace")
    for trace in traces:
        trace_str = ET.tostring(trace, encoding='unicode')
        for term in forbidden_terms:
            assert term not in trace_str, f"Forbidden term '{term}' found in <trace> policy"

def test_readme_security_documentation():
    """Verify that README.md contains required security and usage sections."""
    assert os.path.exists(os.path.join(MODULE_DIR, "README.md"))
    with open(os.path.join(MODULE_DIR, "README.md"), 'r') as f:
        content = f.read()

    assert "## Usage" in content
    assert "### Caller Authentication" in content
    assert "### APIM Subscription" in content
    assert "### Example Usage (Placeholder)" in content
    assert "## Security & State" in content
    assert "### Terraform State Security" in content
    assert "### Safe Telemetry" in content
    assert "Do not commit" in content

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

    # Verify subscription is required
    assert "subscription_required = true" in content

    # Verify policy uses tenant_id, audience, and client_id
    assert "TENANT_ID" in content
    assert "AUDIENCE" in content
    assert "CLIENT_ID" in content
    assert "azurerm_user_assigned_identity.apim_identity.client_id" in content
