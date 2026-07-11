import os
import yaml
import re
import hcl2
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
    uuid_pattern = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")

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
        # This is a bit naive but helps catch hardcoded values that aren't placeholders
        matches = re.findall(pattern, content)
        for match in matches:
            # If it contains a placeholder like ${{ or $( or var., it's probably fine
            if not any(placeholder in match for placeholder in ["${{", "$(", "var.", "sig="]):
                pytest.fail(f"Potential hardcoded secret found in {example_path}: {match}")

def test_github_actions_oidc_permissions():
    gha_path = os.path.join(os.path.dirname(__file__), "..", "examples", "github-actions-deploy.yml")
    if not os.path.exists(gha_path):
        return

    with open(gha_path, "r") as f:
        content = yaml.safe_load(f)

    permissions = content.get("permissions", {})
    assert permissions.get("id-token") == "write", "GitHub Actions example must have 'id-token: write' for OIDC"
    assert permissions.get("contents") == "read", "GitHub Actions example should have 'contents: read'"

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

        # Look for -var="name=..." or -var="name=$(...)" or -var="name=${{...}}"
        var_matches = re.findall(r'-var=["\']([^=]+)=', content)

        for var_name in var_matches:
            # Note: prefix and location are common Terraform vars but might not be in module.yaml
            # However, the task says align with real Web App module contract.
            # Let's check against module.yaml and common base vars.
            allowed_vars = module_inputs + ["prefix", "location"]
            assert var_name in allowed_vars, f"Example {example_path} uses variable '{var_name}' not defined in module.yaml inputs"

def test_no_production_identifiers():
    examples = get_examples()
    # Reject things that look like real production resource names or IDs
    prod_patterns = [
        r"prod-",
        r"-production",
        r"account_key",
    ]

    for example_path in examples:
        with open(example_path, "r") as f:
            content = f.read().lower()
            for pattern in prod_patterns:
                assert not re.search(pattern, content), f"Found production-like identifier '{pattern}' in {example_path}"
