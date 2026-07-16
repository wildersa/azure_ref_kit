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

    # Check for APIM specific inputs/outputs
    input_names = [i["name"] for i in data["inputs"]]
    assert "APIM_NAME" in input_names
    assert "RESOURCE_GROUP_NAME" in input_names
    assert "RESOURCE_PREFIX" in input_names
    assert "AUTH_CLIENT_ID" in input_names

    output_names = [o["name"] for o in data["outputs"]]
    assert "gateway_url" in output_names
    assert "webapp_api_endpoint" in output_names

def test_apim_gateway_workflow_exists():
    workflow_path = pathlib.Path(__file__).parent.parent / "apim-ai-gateway-deploy.yml"
    assert workflow_path.exists(), "apim-ai-gateway-deploy.yml is missing"

def test_apim_gateway_workflow_security():
    workflow_path = pathlib.Path(__file__).parent.parent / "apim-ai-gateway-deploy.yml"
    with open(workflow_path, "r") as f:
        content = f.read()
        data = yaml.safe_load(content)

    # OIDC Check
    assert data["permissions"]["id-token"] == "write"
    assert "azure/login" in content
    assert "client-id: ${{ secrets.AZURE_CLIENT_ID }}" in content

    # No secrets check
    assert "password" not in content.lower()
    assert "client-secret" not in content.lower()

    # Gated apply check
    deploy_job = data["jobs"]["deploy"]
    assert "environment" in deploy_job
    assert deploy_job["environment"] == "apim-gateway-deploy"

    # Plan suppression check
    plan_step = next(s for s in data["jobs"]["plan"]["steps"] if s.get("name") == "Terraform Plan")
    assert "> /dev/null" in plan_step["run"], "Terraform plan output must be suppressed"

    # Apply suppression check
    apply_step = next(s for s in data["jobs"]["deploy"]["steps"] if s.get("name") == "Terraform Apply")
    assert "> /dev/null" in apply_step["run"], "Terraform apply output must be suppressed"

def test_webapp_agent_api_workflow_exists():
    workflow_path = pathlib.Path(__file__).parent.parent / "webapp-agent-api-deploy.yml"
    assert workflow_path.exists(), "webapp-agent-api-deploy.yml is missing"

def test_webapp_agent_api_workflow_security():
    workflow_path = pathlib.Path(__file__).parent.parent / "webapp-agent-api-deploy.yml"
    with open(workflow_path, "r") as f:
        content = f.read()
        data = yaml.safe_load(content)

    # OIDC Check
    assert data["permissions"]["id-token"] == "write"
    assert "azure/login" in content
    assert "client-id: ${{ secrets.AZURE_CLIENT_ID }}" in content

    # No secrets check
    assert "password" not in content.lower()
    assert "client-secret" not in content.lower()

    # Gated apply check
    deploy_job = data["jobs"]["deploy"]
    assert "environment" in deploy_job
    assert deploy_job["environment"] == "webapp-agent-api-deploy"

    # Plan suppression check
    plan_step = next(s for s in data["jobs"]["plan"]["steps"] if s.get("name") == "Terraform Plan")
    assert "> /dev/null" in plan_step["run"], "Terraform plan output must be suppressed"

    # Apply suppression check
    apply_step = next(s for s in data["jobs"]["deploy"]["steps"] if s.get("name") == "Terraform Apply")
    assert "> /dev/null" in apply_step["run"], "Terraform apply output must be suppressed"

def test_readme_contains_required_sections():
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## Deployment Architecture" in content
    assert "```mermaid" in content
    assert "## Configuration and Secrets" in content
    assert "## Cost Impact & Operations" in content
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
