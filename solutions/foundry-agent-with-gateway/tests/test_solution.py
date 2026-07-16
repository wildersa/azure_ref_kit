import os
import yaml
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


def test_solution_yaml_structure():
    """Verify the solution.yaml file exists and has the required fields."""
    solution_file = Path(__file__).parent.parent / "solution.yaml"
    assert solution_file.exists()

    with open(solution_file, "r") as f:
        data = yaml.safe_load(f)

    assert data["name"] == "foundry-agent-with-gateway"
    assert "composition" in data
    assert "building-blocks/gateways/apim-ai-gateway/" in data["composition"]


def test_src_no_secrets():
    """Verify that source code doesn't contain obvious secrets or hardcoded endpoints."""
    src_dir = Path(__file__).parent.parent / "src"
    for file in src_dir.glob("*.py"):
        with open(file, "r") as f:
            content = f.read()
            # Check for generic secret patterns
            # Verify no raw backend keys are mentioned, but allow gateway specific header names
            assert (
                "api_key" not in content.lower()
                or "Ocp-Apim-Subscription-Key" in content
            )
            assert "https://openai.azure.com" not in content
            assert "secret" not in content.lower()


def test_config_validation():
    """Test the configuration loading and validation logic."""
    from src.config import Settings

    # Clear existing env vars to ensure a clean state
    for key in [
        "AZURE_AI_PROJECT_ENDPOINT",
        "AZURE_AI_AGENT_NAME",
        "AZURE_AI_MODEL_NAME",
        "AZURE_AI_GATEWAY_CONNECTION_NAME",
    ]:
        if key in os.environ:
            del os.environ[key]

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
    os.environ["AZURE_AI_GATEWAY_CONNECTION_NAME"] = "ai-gateway"

    with pytest.raises(ValueError, match="Invalid AZURE_AI_AGENT_NAME"):
        Settings.from_env()

    # Valid config
    os.environ["AZURE_AI_AGENT_NAME"] = "valid-agent"
    settings = Settings.from_env()
    assert settings.agent_name == "valid-agent"
    assert settings.model_name == "gpt-4o"
    assert settings.gateway_connection_name == "ai-gateway"


def test_runtime_gateway_contract():
    """Verify the runtime correctly implements the gateway routing and API contracts."""
    from src.config import Settings
    from src.adapter import FoundryAgentAdapter

    # 1. Setup mock settings
    settings = Settings(
        project_endpoint="https://test.ai.azure.com/api/projects/123",
        agent_name="test-agent",
        model_name="gpt-4o",
        gateway_connection_name="ai-gateway-conn",
    )

    adapter = FoundryAgentAdapter(settings)

    # 2. Mock the AIProjectClient and its sub-clients
    with patch("src.adapter.AIProjectClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_agent = MagicMock()
        mock_agent.name = "resolved-agent-id"
        mock_client.agents.create_version.return_value = mock_agent

        mock_openai = MagicMock()
        mock_client.get_openai_client.return_value = mock_openai
        mock_response = MagicMock()
        mock_response.output_text = "Hello from AI"
        mock_openai.responses.create.return_value = mock_response

        # 3. Execute the call
        response = adapter.get_chat_response("Hi")

        # 4. Verify Qualified Model Naming Contract
        # Format must be: <connection-name>/<model-deployment-name>
        expected_model = "ai-gateway-conn/gpt-4o"
        args, kwargs = mock_client.agents.create_version.call_args
        assert kwargs["definition"].model == expected_model

        # 5. Verify Responses API Payload Contract
        # Must use "agent_reference" key in extra_body
        args, kwargs = mock_openai.responses.create.call_args
        assert "agent_reference" in kwargs["extra_body"]
        assert kwargs["extra_body"]["agent_reference"]["name"] == "resolved-agent-id"
        assert kwargs["extra_body"]["agent_reference"]["type"] == "agent_reference"

        assert response == "Hello from AI"


def test_rate_limit_handling():
    """Verify that the adapter correctly handles 429 errors from the gateway."""
    from src.config import Settings
    from src.adapter import FoundryAgentAdapter

    settings = Settings(
        project_endpoint="https://test.ai.azure.com/api/projects/123",
        agent_name="test-agent",
        model_name="gpt-4o",
        gateway_connection_name="ai-gateway-conn",
    )
    adapter = FoundryAgentAdapter(settings)

    with patch("src.adapter.AIProjectClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_agent = MagicMock()
        mock_client.agents.create_version.return_value = mock_agent

        mock_openai = MagicMock()
        mock_client.get_openai_client.return_value = mock_openai

        # Simulate a 429 Too Many Requests error
        mock_openai.responses.create.side_effect = Exception(
            "Status 429: Too Many Requests"
        )

        with pytest.raises(
            RuntimeError, match="The agent is currently busy due to high demand"
        ):
            adapter.get_chat_response("Hi")


def test_terraform_constraints():
    """Verify that the Terraform configuration adheres to the required constraints."""
    infra_dir = Path(__file__).parent.parent / "infra" / "terraform"
    main_tf = infra_dir / "main.tf"
    assert main_tf.exists()

    with open(main_tf, "r") as f:
        content = f.read()

    # Must NOT call the gateway module (should consume existing contract)
    assert 'module "ai_gateway"' not in content
    assert "apim-ai-gateway/infra/terraform" not in content

    # Must NOT be shared globally (least privilege)
    assert "isSharedToAll = false" in content

    # Must scope the connection to a project parent
    assert "parent_id = var.foundry_project_id" in content

    # Verify least-privilege subscription scope
    assert "api_id = var.gateway_api_id" in content


def test_mermaid_diagram_exists():
    """Verify README.md contains the Mermaid diagram."""
    readme_file = Path(__file__).parent.parent / "README.md"
    assert readme_file.exists()
    with open(readme_file, "r") as f:
        content = f.read()
    assert "```mermaid" in content
    assert "Foundry Agent Service" in content
    assert "APIM AI Gateway" in content
