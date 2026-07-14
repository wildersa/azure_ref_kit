import os
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    """Configuration settings for the Foundry Agent with AI Gateway solution."""

    project_endpoint: str
    agent_name: str
    model_name: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Loads and validates settings from environment variables."""
        project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        agent_name = os.getenv("AZURE_AI_AGENT_NAME")
        model_name = os.getenv("AZURE_AI_MODEL_NAME")

        missing = []
        if not project_endpoint:
            missing.append("AZURE_AI_PROJECT_ENDPOINT")
        if not agent_name:
            missing.append("AZURE_AI_AGENT_NAME")
        if not model_name:
            missing.append("AZURE_AI_MODEL_NAME")

        if missing:
            raise ValueError(
                f"Missing required configuration environment variables: {', '.join(missing)}"
            )

        # Strict validation for agent and model names
        # Constraints: 1-64 chars, alphanumeric, hyphens, or underscores
        name_regex = r"^[a-zA-Z0-9_\-]{1,64}$"
        if not re.match(name_regex, agent_name):
            raise ValueError(
                "Invalid AZURE_AI_AGENT_NAME. Must be 1-64 characters and contain only "
                "alphanumeric, hyphens, or underscores."
            )
        if not re.match(name_regex, model_name):
            raise ValueError(
                "Invalid AZURE_AI_MODEL_NAME. Must be 1-64 characters and contain only "
                "alphanumeric, hyphens, or underscores."
            )

        # Deterministic validation for project endpoint
        parsed = urlparse(project_endpoint)
        if parsed.scheme != "https":
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT must use HTTPS.")
        if parsed.username or parsed.password:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT must not contain credentials.")
        if parsed.query or parsed.fragment:
            raise ValueError(
                "AZURE_AI_PROJECT_ENDPOINT must not contain query or fragment."
            )

        # Expected path: /api/projects/<project-id>
        if not re.match(r"^/api/projects/[a-zA-Z0-9_\-]+$", parsed.path):
            raise ValueError(
                "Invalid AZURE_AI_PROJECT_ENDPOINT path. "
                "Expected format: https://<resource>.ai.azure.com/api/projects/<project-id>"
            )

        return cls(
            project_endpoint=project_endpoint,
            agent_name=agent_name,
            model_name=model_name,
        )


def validate_user_input(user_input: Optional[str]) -> str:
    """Validates the user input prompt for safety and presence."""
    if not user_input or not user_input.strip():
        raise ValueError("User input cannot be empty.")

    # Prevent extremely long inputs
    if len(user_input) > 2000:
        raise ValueError(
            "User input exceeds the maximum allowed length of 2000 characters."
        )

    # Basic check for suspicious patterns (minimal)
    # Note: Full safety is handled by the model's content filters and system instructions.
    if re.search(r"ignore previous instructions", user_input, re.IGNORECASE):
        raise ValueError("Suspicious input detected.")

    return user_input.strip()
