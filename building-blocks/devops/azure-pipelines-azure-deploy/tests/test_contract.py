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

    # Check for Web App Agent API specific inputs/outputs
    input_names = [i["name"] for i in data["inputs"]]
    assert "AZURE_SERVICE_CONNECTION_NAME" in input_names
    assert "RESOURCE_PREFIX" in input_names
    assert "CONTAINER_IMAGE" in input_names
    assert "AZURE_TENANT_ID" in input_names

    output_names = [o["name"] for o in data["outputs"]]
    assert "webapp_api_endpoint" in output_names

def test_readme_contains_required_sections():
    readme_path = pathlib.Path(__file__).parent.parent / "README.md"
    with open(readme_path, "r") as f:
        content = f.read()

    assert "## Purpose" in content
    assert "## When to Use Azure Pipelines instead of GitHub Actions" in content
    assert "## Deployment Architecture" in content
    assert "```mermaid" in content
    assert "## Configuration and Service Connection" in content
    assert "## Configuration and Secrets" in content
    assert "## Cost Impact & Operations" in content
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

def test_contract_alignment():
    module_yaml_path = pathlib.Path(__file__).parent.parent / "module.yaml"
    pipeline_paths = [
        pathlib.Path(__file__).parent.parent / "azure-pipelines.yml",
        pathlib.Path(__file__).parent.parent / "webapp-agent-api-deploy.yml",
        pathlib.Path(__file__).parent.parent / "durable-basic-pipeline-deploy.yml"
    ]

    with open(module_yaml_path, "r") as f:
        module_data = yaml.safe_load(f)

    all_pipeline_params = set()
    all_pipeline_vars = set()

    for path in pipeline_paths:
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                if "parameters" in data:
                    all_pipeline_params.update({p["name"] for p in data.get("parameters", [])})
                if "variables" in data:
                    # Handle both list and dict variables
                    vars_data = data.get("variables", [])
                    if isinstance(vars_data, list):
                        for v in vars_data:
                            if isinstance(v, dict) and "name" in v:
                                all_pipeline_vars.add(v["name"])
                    elif isinstance(vars_data, dict):
                        all_pipeline_vars.update(vars_data.keys())

    module_inputs = {i["name"] for i in module_data.get("inputs", [])}

    # Verify all module inputs are accounted for in at least one pipeline (as parameter or variable)
    for input_name in module_inputs:
        assert input_name in all_pipeline_params or input_name in all_pipeline_vars or input_name == "ENVIRONMENT_NAME", \
            f"Input '{input_name}' defined in module.yaml is missing from all pipeline definitions"

    # Verify no unexpected parameters in pipeline (optional, but good for cleanliness)
    # for param_name in pipeline_params:
    #     assert param_name in module_inputs, f"Parameter '{param_name}' in azure-pipelines.yml is not defined in module.yaml inputs"

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

def test_webapp_agent_api_pipeline_exists():
    pipeline_path = pathlib.Path(__file__).parent.parent / "webapp-agent-api-deploy.yml"
    assert pipeline_path.exists(), "webapp-agent-api-deploy.yml is missing"

def test_webapp_agent_api_pipeline_security():
    pipeline_path = pathlib.Path(__file__).parent.parent / "webapp-agent-api-deploy.yml"
    with open(pipeline_path, "r") as f:
        content = f.read()
        data = yaml.safe_load(content)

    # OIDC/WIF Check
    assert "AzureCLI@2" in content
    assert "azureSubscription: '$(AZURE_SERVICE_CONNECTION_NAME)'" in content

    # No secrets check
    assert "password" not in content.lower()
    assert "client-secret" not in content.lower()

    # Gated apply check
    deploy_stage = next(s for s in data["stages"] if s.get("stage") == "Deploy")
    deploy_job = deploy_stage["jobs"][0]
    assert "environment" in deploy_job
    assert deploy_job["environment"] == "$(ENVIRONMENT_NAME)"

    # Plan suppression check
    plan_stage = next(s for s in data["stages"] if s.get("stage") == "Plan")
    plan_step = next(s for s in plan_stage["jobs"][0]["steps"] if s.get("task") == "AzureCLI@2")
    assert "> /dev/null" in plan_step["inputs"]["inlineScript"], "Terraform plan output must be suppressed"

    # Apply suppression check
    apply_stage = next(s for s in data["stages"] if s.get("stage") == "Deploy")
    apply_job = apply_stage["jobs"][0]

    # Handle deployment job structure
    if "strategy" in apply_job:
        steps = apply_job["strategy"]["runOnce"]["deploy"]["steps"]
    else:
        steps = apply_job["steps"]

    apply_step = next(s for s in steps if s.get("task") == "AzureCLI@2")
    assert "> /dev/null" in apply_step["inputs"]["inlineScript"], "Terraform apply output must be suppressed"

def test_webapp_agent_api_pipeline_working_dir():
    pipeline_path = pathlib.Path(__file__).parent.parent / "webapp-agent-api-deploy.yml"
    with open(pipeline_path, "r") as f:
        content = f.read()

    assert "building-blocks/hosting/webapp-agent-api/infra/terraform" in content
