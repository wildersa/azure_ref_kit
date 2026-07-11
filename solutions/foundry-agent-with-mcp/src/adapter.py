import logging
from typing import Any, Optional

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from openai.types.responses.response_input_param import (
    McpApprovalResponse,
    ResponseInputParam,
)

from .config import Settings
from .agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions

# Redact technical details in logs
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FoundryAgentAdapter:
    """Adapter for the Azure AI Projects SDK with MCP tool support."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._project_client: Optional[AIProjectClient] = None

    def initialize_client(self) -> None:
        """Initializes the AIProjectClient using DefaultAzureCredential."""
        try:
            self._project_client = AIProjectClient(
                endpoint=self.settings.project_endpoint,
                credential=DefaultAzureCredential(),
            )
        except Exception:
            # Customer-Safe Logging: Redact technical details
            logger.error("Failed to initialize AI Project Client.")
            raise RuntimeError("Could not connect to the Azure AI service.")

    def create_or_resolve_agent(self) -> Any:
        """Creates or resolves a Prompt Agent version with MCP tools."""
        if not self._project_client:
            self.initialize_client()

        try:
            # We assume self._project_client is initialized here
            return self._project_client.agents.create_version(  # type: ignore
                agent_name=self.settings.agent_name,
                definition=PromptAgentDefinition(
                    model=self.settings.model_name,
                    instructions=SYSTEM_INSTRUCTIONS,
                    tools=get_tool_definitions(self.settings),
                ),
            )
        except Exception:
            # Customer-Safe Logging: Do NOT log the agent name on failure
            logger.error("Failed to resolve agent.")
            raise RuntimeError("The agent service encountered an error.")

    def get_chat_response(self, user_input: str) -> str:
        """Invokes the agent and handles MCP approval loop."""
        if not self._project_client:
            self.initialize_client()

        try:
            agent = self.create_or_resolve_agent()

            with self._project_client.get_openai_client() as openai_client:  # type: ignore
                # Initial request
                response = openai_client.responses.create(
                    input=user_input,
                    extra_body={
                        "agent_reference": {
                            "name": agent.name,
                            "type": "agent_reference",
                        }
                    },
                )

                # Loop to handle MCP approvals (max 5 iterations)
                for _ in range(5):
                    input_list: ResponseInputParam = []
                    approval_requests = [
                        item
                        for item in response.output
                        if item.type == "mcp_approval_request"
                    ]

                    if not approval_requests:
                        break

                    for req in approval_requests:
                        # Security check: verify server label and tool name against allowlist
                        # Note: req.name might be available depending on SDK version
                        tool_name = getattr(req, "name", None)
                        is_allowed_server = (
                            req.server_label == self.settings.mcp_server_label
                        )
                        is_allowed_tool = (
                            tool_name in self.settings.allowed_tool_names
                            if tool_name
                            else False
                        )

                        if is_allowed_server and is_allowed_tool:
                            # Auto-approve for this reference implementation after validation
                            input_list.append(
                                McpApprovalResponse(
                                    type="mcp_approval_response",
                                    approve=True,
                                    approval_request_id=req.id,
                                )
                            )
                        else:
                            logger.warning("Agent requested unauthorized MCP tool.")
                            input_list.append(
                                McpApprovalResponse(
                                    type="mcp_approval_response",
                                    approve=False,
                                    approval_request_id=req.id,
                                )
                            )

                    if not input_list:
                        break

                    # Submit approvals back to the agent
                    response = openai_client.responses.create(
                        input=input_list,
                        previous_response_id=response.id,
                        extra_body={
                            "agent_reference": {
                                "name": agent.name,
                                "type": "agent_reference",
                            }
                        },
                    )

                output_text = response.output_text
                if not output_text or not str(output_text).strip():
                    logger.error("Agent returned an empty or missing response.")
                    raise RuntimeError("The agent was unable to provide a response.")

                return str(output_text)

        except RuntimeError:
            raise
        except Exception:
            logger.error("Error during response generation.")
            # Sanitize failures: do not return stack traces or raw provider payloads
            raise RuntimeError("The agent was unable to provide a response.")
