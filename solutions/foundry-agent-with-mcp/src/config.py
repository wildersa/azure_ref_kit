import os
import re
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    """Configuration settings for the Foundry Agent with MCP solution."""

    project_endpoint: str
    agent_name: str
    model_name: str
    mcp_server_url: str
    mcp_server_label: str
    allowed_tool_names: List[str]

    @classmethod
    def from_env(cls) -> "Settings":
        """Loads and validates settings from environment variables."""
        project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        agent_name = os.getenv("AZURE_AI_AGENT_NAME")
        model_name = os.getenv("AZURE_AI_MODEL_NAME")
        mcp_server_url = os.getenv("MCP_SERVER_URL")
        mcp_server_label = os.getenv("MCP_SERVER_LABEL")
        allowed_tools_raw = os.getenv("ALLOWED_TOOL_NAMES", "")

        missing = []
        if not project_endpoint:
            missing.append("AZURE_AI_PROJECT_ENDPOINT")
        if not agent_name:
            missing.append("AZURE_AI_AGENT_NAME")
        if not model_name:
            missing.append("AZURE_AI_MODEL_NAME")
        if not mcp_server_url:
            missing.append("MCP_SERVER_URL")
        if not mcp_server_label:
            missing.append("MCP_SERVER_LABEL")
        if not allowed_tools_raw:
            missing.append("ALLOWED_TOOL_NAMES")

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
        if not re.match(name_regex, mcp_server_label):
            raise ValueError(
                "Invalid MCP_SERVER_LABEL. Must be 1-64 characters and contain only "
                "alphanumeric, hyphens, or underscores."
            )

        # Deterministic validation for project endpoint
        parsed_endpoint = urlparse(project_endpoint)
        if parsed_endpoint.scheme != "https":
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT must use HTTPS.")
        if parsed_endpoint.username or parsed_endpoint.password:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT must not contain credentials.")
        if parsed_endpoint.query or parsed_endpoint.fragment:
            raise ValueError(
                "AZURE_AI_PROJECT_ENDPOINT must not contain query or fragment."
            )
        if not re.match(r"^/api/projects/[a-zA-Z0-9_\-]+$", parsed_endpoint.path):
            raise ValueError(
                "Invalid AZURE_AI_PROJECT_ENDPOINT path. "
                "Expected format: https://<resource>.ai.azure.com/api/projects/<project-id>"
            )

        # Deterministic validation for MCP server URL
        parsed_mcp = urlparse(mcp_server_url)
        if parsed_mcp.scheme not in ("http", "https"):
            raise ValueError("MCP_SERVER_URL must use HTTP or HTTPS.")
        if parsed_mcp.username or parsed_mcp.password:
            raise ValueError("MCP_SERVER_URL must not contain credentials.")

        # Security: HTTP is only allowed for localhost/127.0.0.1
        if parsed_mcp.scheme == "http":
            hostname = parsed_mcp.hostname
            if hostname not in ("localhost", "127.0.0.1"):
                raise ValueError("HTTP MCP_SERVER_URL is only allowed for localhost.")

        allowed_tool_names = [
            t.strip() for t in allowed_tools_raw.split(",") if t.strip()
        ]
        if not allowed_tool_names:
            raise ValueError("ALLOWED_TOOL_NAMES must contain at least one tool name.")

        # Validate each tool name in the allowlist
        for tool_name in allowed_tool_names:
            if not re.match(r"^[a-zA-Z0-9_\-]{1,64}$", tool_name):
                raise ValueError(
                    f"Invalid tool name in ALLOWED_TOOL_NAMES: {tool_name}"
                )

        return cls(
            project_endpoint=project_endpoint,
            agent_name=agent_name,
            model_name=model_name,
            mcp_server_url=mcp_server_url,
            mcp_server_label=mcp_server_label,
            allowed_tool_names=allowed_tool_names,
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
    if re.search(r"ignore previous instructions", user_input, re.IGNORECASE):
        raise ValueError("Suspicious input detected.")

    return user_input.strip()
