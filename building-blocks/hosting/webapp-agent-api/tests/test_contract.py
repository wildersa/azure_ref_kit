import os
import yaml
import re


def test_module_yaml_exists_and_valid():
    module_yaml_path = os.path.join(os.path.dirname(__file__), "..", "module.yaml")
    assert os.path.exists(module_yaml_path)

    with open(module_yaml_path, "r") as f:
        content = yaml.safe_load(f)

    assert content["name"] == "webapp-agent-api"
    assert content["type"] == "building-block"
    assert "security_boundary" in content
    assert "customer_safe_boundary" in content
    assert content["security_boundary"]["enforce_easy_auth"] is True


def test_readme_has_required_sections():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    assert os.path.exists(readme_path)

    with open(readme_path, "r") as f:
        content = f.read()

    required_sections = [
        "## Purpose",
        "## Scenario",
        "## Architecture",
        "## Comparison: App Service vs. Alternatives",
        "## Security and Safety",
        "## API Contract",
        "## Configuration",
        "## Local Development",
        "## Azure Hosting Notes",
        "## Validation Commands",
        "## Microsoft Documentation Consulted",
    ]

    for section in required_sections:
        assert section in content, f"Missing required section: {section}"


def test_readme_has_mermaid_diagram():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    with open(readme_path, "r") as f:
        content = f.read()

    assert "```mermaid" in content
    assert "flowchart" in content


def test_no_unsafe_output_wording():
    # Check README and module.yaml for words that might suggest unsafe behavior
    files_to_check = [
        os.path.join(os.path.dirname(__file__), "..", "README.md"),
        os.path.join(os.path.dirname(__file__), "..", "module.yaml"),
    ]

    unsafe_patterns = [
        r"expose raw logs",
        r"return secrets",
        r"disable security",
        r"publicly accessible storage",
        r"azure_openai_key",
        r"your-key",
    ]

    for file_path in files_to_check:
        with open(file_path, "r") as f:
            content = f.read().lower()
            for pattern in unsafe_patterns:
                assert not re.search(pattern, content), (
                    f"Found unsafe pattern '{pattern}' in {file_path}"
                )


def test_terraform_security_defaults():
    main_tf_path = os.path.join(
        os.path.dirname(__file__), "..", "infra", "terraform", "main.tf"
    )
    assert os.path.exists(main_tf_path)

    with open(main_tf_path, "r") as f:
        content = f.read()

    # Verify security defaults in Terraform
    assert "auth_settings_v2" in content
    assert "auth_enabled           = true" in content
    assert "https_only = true" in content
    assert "unauthenticated_action = \"Return401\"" in content
    assert "tenant_auth_endpoint = \"https://login.microsoftonline.com/${var.tenant_id}/v2.0\"" in content
