import yaml
from pathlib import Path


def test_azure_yaml_exists():
    """Verify that azure.yaml exists in the solution root."""
    solution_root = Path(__file__).parent.parent
    azure_yaml_path = solution_root / "azure.yaml"
    assert azure_yaml_path.exists(), "azure.yaml must exist in the solution root."


def test_azure_yaml_structure():
    """Verify the structure and content of azure.yaml."""
    solution_root = Path(__file__).parent.parent
    azure_yaml_path = solution_root / "azure.yaml"

    with open(azure_yaml_path, "r") as f:
        config = yaml.safe_load(f)

    assert config.get("name") == "foundry-agent-basic", "Project name must be 'foundry-agent-basic'."

    infra = config.get("infra")
    assert infra is not None, "Infra section must exist."
    assert infra.get("provider") == "terraform", "Infra provider must be 'terraform'."

    infra_path = infra.get("path")
    assert infra_path is not None, "Infra path must be specified."

    # Resolve relative path from solution root
    resolved_infra_path = (solution_root / infra_path).resolve()
    assert resolved_infra_path.exists(), f"Infra path {resolved_infra_path} does not exist."
    assert resolved_infra_path.is_dir(), f"Infra path {resolved_infra_path} is not a directory."

    # Ensure it's the expected terraform directory
    main_tf = resolved_infra_path / "main.tf"
    assert main_tf.exists(), f"main.tf not found in {resolved_infra_path}."


def test_no_forbidden_files_referenced():
    """Verify that no sensitive or forbidden files are referenced in azure.yaml."""
    solution_root = Path(__file__).parent.parent
    azure_yaml_path = solution_root / "azure.yaml"

    with open(azure_yaml_path, "r") as f:
        content = f.read()

    forbidden_patterns = [
        ".tfstate",
        "terraform.tfvars",
        ".env",
        "secret",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Forbidden pattern '{pattern}' found in azure.yaml."

def test_infra_directory_contains_no_state():
    """Ensure the infra directory does not contain terraform state files."""
    solution_root = Path(__file__).parent.parent
    infra_path = solution_root / "infra" / "terraform"

    state_files = list(infra_path.glob("*.tfstate*"))
    assert not state_files, f"Found terraform state files in {infra_path}: {state_files}"

def test_terraform_outputs_mapping():
    """Verify that Terraform outputs match the required environment variables."""
    solution_root = Path(__file__).parent.parent
    outputs_tf_path = solution_root / "infra" / "terraform" / "outputs.tf"

    assert outputs_tf_path.exists(), "outputs.tf must exist."

    with open(outputs_tf_path, "r") as f:
        content = f.read()

    # We expect AZURE_AI_PROJECT_ENDPOINT to be defined as an output
    # so that azd can map it to the environment variable of the same name.
    assert 'output "AZURE_AI_PROJECT_ENDPOINT"' in content, (
        "Terraform must output AZURE_AI_PROJECT_ENDPOINT for azd mapping."
    )
