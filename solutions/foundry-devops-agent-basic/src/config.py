import os
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    """Configuration settings for the Foundry DevOps Status Agent solution."""

    # Azure AI Foundry configuration
    project_endpoint: str
    agent_name: str
    model_name: str

    # Azure DevOps configuration
    devops_pat: str
    organization_url: str
    project: str
    build_id: int

    @classmethod
    def from_env(cls) -> "Settings":
        """Loads and validates settings from environment variables."""
        # Azure AI
        project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        agent_name = os.getenv("AZURE_AI_AGENT_NAME")
        model_name = os.getenv("AZURE_AI_MODEL_NAME")

        # Azure DevOps
        devops_pat = os.getenv("AZURE_DEVOPS_PAT")
        organization_url = os.getenv("AZURE_DEVOPS_ORG_URL")
        project = os.getenv("AZURE_DEVOPS_PROJECT")
        build_id_str = os.getenv("AZURE_DEVOPS_BUILD_ID")

        missing = []
        if not project_endpoint:
            missing.append("AZURE_AI_PROJECT_ENDPOINT")
        if not agent_name:
            missing.append("AZURE_AI_AGENT_NAME")
        if not model_name:
            missing.append("AZURE_AI_MODEL_NAME")
        if not devops_pat:
            missing.append("AZURE_DEVOPS_PAT")
        if not organization_url:
            missing.append("AZURE_DEVOPS_ORG_URL")
        if not project:
            missing.append("AZURE_DEVOPS_PROJECT")
        if not build_id_str:
            missing.append("AZURE_DEVOPS_BUILD_ID")

        if missing:
            raise ValueError(
                f"Missing required configuration environment variables: {', '.join(missing)}"
            )

        # Validation for agent and model names
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

        # Validation for project endpoint
        parsed_project = urlparse(project_endpoint)
        if parsed_project.scheme != "https":
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT must use HTTPS.")
        if not re.match(r"^/api/projects/[a-zA-Z0-9_\-]+$", parsed_project.path):
            raise ValueError(
                "Invalid AZURE_AI_PROJECT_ENDPOINT path. "
                "Expected format: https://<resource>.ai.azure.com/api/projects/<project-id>"
            )

        # Validation for organization URL
        parsed_org = urlparse(organization_url)
        if parsed_org.scheme != "https":
            raise ValueError("AZURE_DEVOPS_ORG_URL must use HTTPS.")
        if not (
            parsed_org.netloc == "dev.azure.com"
            or parsed_org.netloc.endswith(".visualstudio.com")
        ):
            raise ValueError("AZURE_DEVOPS_ORG_URL must be a valid Azure DevOps URL.")

        # Validation for build ID
        try:
            build_id = int(build_id_str)
            if build_id <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError("AZURE_DEVOPS_BUILD_ID must be a positive integer.")

        return cls(
            project_endpoint=project_endpoint,
            agent_name=agent_name,
            model_name=model_name,
            devops_pat=devops_pat,
            organization_url=organization_url,
            project=project,
            build_id=build_id,
        )


def validate_user_input(user_input: Optional[str]) -> str:
    """Validates the user input prompt for safety and presence."""
    if not user_input or not user_input.strip():
        raise ValueError("User input cannot be empty.")

    if len(user_input) > 2000:
        raise ValueError(
            "User input exceeds the maximum allowed length of 2000 characters."
        )

    if re.search(r"ignore previous instructions", user_input, re.IGNORECASE):
        raise ValueError("Suspicious input detected.")

    return user_input.strip()
