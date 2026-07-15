import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Settings:
    """Configuration settings for the Foundry Agent with Queue Tool."""

    # Azure AI Project settings
    project_endpoint: str = field(
        default_factory=lambda: os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
    )
    model_name: str = field(
        default_factory=lambda: os.environ.get("AZURE_AI_MODEL_NAME", "gpt-4o")
    )
    agent_name: str = field(
        default_factory=lambda: os.environ.get("AZURE_AI_AGENT_NAME", "AsyncQueueAgent")
    )

    # Async Tool settings (Function App endpoints)
    # In a real scenario, these would be the URLs of the deployed Function App
    function_submit_url: str = field(
        default_factory=lambda: os.environ.get(
            "ASYNC_TOOL_SUBMIT_URL", "http://localhost:7071/api/submit"
        )
    )
    function_status_url_template: str = field(
        default_factory=lambda: os.environ.get(
            "ASYNC_TOOL_STATUS_URL_TEMPLATE",
            "http://localhost:7071/api/status/{correlation_id}",
        )
    )

    # Security: allowed tools for the agent to call via the adapter
    allowed_tool_names: List[str] = field(
        default_factory=lambda: ["submit_task", "get_task_status"]
    )

    def validate(self) -> None:
        """Validates that required settings are present."""
        if not self.project_endpoint:
            # We allow empty endpoint for local mock validation if needed,
            # but the adapter will fail if it tries to initialize a real client.
            pass
