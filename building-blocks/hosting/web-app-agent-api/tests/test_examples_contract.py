import os
import yaml
import re
import pytest


def get_examples():
    examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
    examples = []
    if not os.path.exists(examples_dir):
        return []
    for f in os.listdir(examples_dir):
        if f.endswith(".yml") or f.endswith(".yaml"):
            examples.append(os.path.join(examples_dir, f))
    return examples


@pytest.mark.parametrize("example_path", get_examples())
def test_example_no_literal_uuids(example_path):
    with open(example_path, "r") as f:
        content = f.read()

    # UUID pattern
    uuid_pattern = re.compile(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    )

    # Find all UUIDs
    matches = uuid_pattern.findall(content)

    # We want to reject ANY literal UUID in these examples to ensure they use placeholders
    assert not matches, f"Found literal UUIDs in {example_path}: {matches}. Use placeholders or secret references instead."


@pytest.mark.parametrize("example_path", get_examples())
def test_example_no_secrets_or_keys(example_path):
    with open(example_path, "r") as f:
        content = f.read().lower()

    forbidden_patterns = [
        r"password\s*[:=]\s*[^\s}]+",
        r"secret\s*[:=]\s*[^\s}]+",
        r"key\s*[:=]\s*[^\s}]+",
        r"connectionstring\s*[:=]\s*[^\s}]+",
    ]

    for pattern in forbidden_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if not any(
                placeholder in match for placeholder in ["${{", "$(", "var.", "sig="]
            ):
                pytest.fail(
                    f"Potential hardcoded secret found in {example_path}: {match}"
                )


def test_github_actions_oidc_permissions():
    gha_path = os.path.join(
        os.path.dirname(__file__), "..", "examples", "github-actions-deploy.yml"
    )
    if not os.path.exists(gha_path):
        return

    with open(gha_path, "r") as f:
        content = yaml.safe_load(f)

    permissions = content.get("permissions", {})
    assert (
        permissions.get("id-token") == "write"
    ), "GitHub Actions example must have 'id-token: write' for OIDC"
    assert (
        permissions.get("contents") == "read"
    ), "GitHub Actions example should have 'contents: read'"


def test_examples_use_valid_module_inputs():
    module_root = os.path.join(os.path.dirname(__file__), "..")
    module_yaml_path = os.path.join(module_root, "module.yaml")

    with open(module_yaml_path, "r") as f:
        module_config = yaml.safe_load(f)

    module_inputs = [i["name"] for i in module_config.get("inputs", [])]

    examples = get_examples()
    for example_path in examples:
        with open(example_path, "r") as f:
            content = f.read()

        var_matches = re.findall(r'-var=["\']([^=]+)=', content)

        for var_name in var_matches:
            allowed_vars = module_inputs + ["prefix", "location"]
            assert (
                var_name in allowed_vars
            ), f"Example {example_path} uses variable '{var_name}' not defined in module.yaml inputs"


@pytest.mark.parametrize("example_path", get_examples())
def test_no_production_or_literal_backend_identifiers(example_path):
    with open(example_path, "r") as f:
        content = f.read().lower()

    # Reject things that look like real production resource names or literal backend/state values
    forbidden_patterns = [
        r"prod-",
        r"-production",
        r"account_key",
        r"rg-terraform-state",  # Literal backend resource group
        r"stterraformstate",  # Literal backend storage account
        r"tfstate",  # Literal backend container
        r"\.tfstate",  # Literal state file extension (if hardcoded)
    ]

    for pattern in forbidden_patterns:
        # Check if pattern exists in content
        if re.search(pattern, content):
            # Check if it's within a placeholder
            matches = re.finditer(pattern, content)
            for match in matches:
                # Get some context around the match
                start = max(0, match.start() - 10)
                end = min(len(content), match.end() + 10)
                context = content[start:end]

                # If it's not wrapped in placeholders, it's a literal violation
                if not ("${{" in context or "$(" in context):
                    pytest.fail(
                        f"Found forbidden literal or production-like identifier '{pattern}' in {example_path} at context: ...{context}..."
                    )
