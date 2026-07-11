import os
import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    """Configuration settings for the Foundry Agent Basic solution."""

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

        # Basic validation for endpoint format
        if (
            not project_endpoint.startswith("https://")
            or "/api/projects/" not in project_endpoint
        ):
            raise ValueError(
                "Invalid AZURE_AI_PROJECT_ENDPOINT format. "
                "Expected: https://<resource>.ai.azure.com/api/projects/<project-id>"
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
    # Here we just do a basic sanity check.
    if re.search(r"ignore previous instructions", user_input, re.IGNORECASE):
        raise ValueError("Suspicious input detected.")

    return user_input.strip()
