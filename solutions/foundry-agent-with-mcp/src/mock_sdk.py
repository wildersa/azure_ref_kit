"""
Mock objects for Azure AI Projects SDK to support local validation.
"""

from typing import List, Optional


class Tool:
    """Base class for all tools."""

    def __init__(self, type: str):
        self.type = type


class MCPTool(Tool):
    """Mock for MCPTool."""

    def __init__(
        self,
        server_label: str,
        server_url: str,
        require_approval: Optional[str] = "always",
        project_connection_id: Optional[str] = None,
        allowed_tools: Optional[List[str]] = None,
    ):
        super().__init__(type="mcp")
        self.server_label = server_label
        self.server_url = server_url
        self.require_approval = require_approval
        self.project_connection_id = project_connection_id
        self.allowed_tools = allowed_tools
