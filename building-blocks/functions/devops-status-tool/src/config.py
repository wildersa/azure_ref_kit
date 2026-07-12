import os
import re
from dataclasses import dataclass
from pydantic import HttpUrl


@dataclass(frozen=True)
class Settings:
    """Configuration settings for the DevOps Status Tool."""

    devops_pat: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Loads and validates settings from environment variables."""
        devops_pat = os.getenv("AZURE_DEVOPS_PAT")

        if not devops_pat:
            raise ValueError("Missing required configuration: AZURE_DEVOPS_PAT")

        # Basic PAT validation (usually 52 or 100+ chars base64-like)
        if len(devops_pat) < 20:
            raise ValueError("AZURE_DEVOPS_PAT appears too short to be valid.")

        return cls(devops_pat=devops_pat)


def validate_organization_url(url: HttpUrl) -> None:
    """
    Validates that the organization URL follows Azure DevOps standards.
    Supports https://dev.azure.com/{org} and https://{org}.visualstudio.com
    """
    url_str = str(url)

    # Standard dev.azure.com pattern
    dev_azure_pattern = r"^https://dev\.azure\.com/[a-zA-Z0-9_\-]+/?$"
    # Legacy visualstudio.com pattern
    vs_pattern = r"^https://[a-zA-Z0-9_\-]+\.visualstudio\.com/?$"

    if not (re.match(dev_azure_pattern, url_str) or re.match(vs_pattern, url_str)):
        raise ValueError(
            "Invalid organization URL. Must be in the format 'https://dev.azure.com/{org}' "
            "or 'https://{org}.visualstudio.com'."
        )


def validate_project_identifier(project: str) -> None:
    """Validates the project name or ID for safety and format."""
    if not project or not project.strip():
        raise ValueError("Project identifier cannot be empty.")

    # Project names are usually 1-64 characters, alphanumeric, spaces, hyphens, underscores.
    # We use a reasonably safe pattern to prevent injection or weirdness.
    # Project IDs are UUIDs.
    project_regex = r"^[a-zA-Z0-9_\-\. ]{1,64}$"
    uuid_regex = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

    if not (re.match(project_regex, project) or re.match(uuid_regex, project.lower())):
        raise ValueError(
            "Invalid project identifier. Must be 1-64 characters (alphanumeric, spaces, ., -, _) "
            "or a valid UUID."
        )
