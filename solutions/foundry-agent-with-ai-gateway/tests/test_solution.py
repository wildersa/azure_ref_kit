import os
import yaml
import pytest
from pathlib import Path


def test_solution_yaml_structure():
    """Verify the solution.yaml file exists and has the required fields."""
    solution_file = Path(__file__).parent.parent / "solution.yaml"
    assert solution_file.exists()

    with open(solution_file, "r") as f:
        data = yaml.safe_load(f)

    assert data["name"] == "foundry-agent-with-ai-gateway"
    assert "composition" in data
    assert "building-blocks/gateways/apim-ai-gateway/" in data["composition"]


def test_src_no_secrets():
    """Verify that source code doesn't contain obvious secrets or hardcoded endpoints."""
    src_dir = Path(__file__).parent.parent / "src"
    for file in src_dir.glob("*.py"):
        with open(file, "r") as f:
            content = f.read()
            # Check for generic secret patterns
            assert (
                "api_key" not in content.lower()
                or "Ocp-Apim-Subscription-Key" in content
                or "api-key" in content
            )
            assert "https://openai.azure.com" not in content
            assert "secret" not in content.lower()


def test_config_validation():
    """Test the configuration loading and validation logic."""
    from src.config import Settings

    # Missing env vars
    with pytest.raises(
        ValueError, match="Missing required configuration environment variables"
    ):
        Settings.from_env()

    # Invalid agent name
    os.environ["AZURE_AI_PROJECT_ENDPOINT"] = (
        "https://test.ai.azure.com/api/projects/123"
    )
    os.environ["AZURE_AI_AGENT_NAME"] = "invalid name!"
    os.environ["AZURE_AI_MODEL_NAME"] = "gpt-4o"

    with pytest.raises(ValueError, match="Invalid AZURE_AI_AGENT_NAME"):
        Settings.from_env()

    # Valid config
    os.environ["AZURE_AI_AGENT_NAME"] = "valid-agent"
    settings = Settings.from_env()
    assert settings.agent_name == "valid-agent"
    assert settings.model_name == "gpt-4o"


def test_mermaid_diagram_exists():
    """Verify README.md contains the Mermaid diagram."""
    readme_file = Path(__file__).parent.parent / "README.md"
    assert readme_file.exists()
    with open(readme_file, "r") as f:
        content = f.read()
    assert "```mermaid" in content
    assert "Foundry Agent Service" in content
    assert "APIM AI Gateway" in content
