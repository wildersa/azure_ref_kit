import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    ResponseInputParam,
)

from .config import Settings
from .agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions

# Add the building block to the path to allow importing the tool implementation
# This allows us to reuse the tool without duplicating the code.
REPO_ROOT = Path(__file__).parent.parent.parent.parent
DEVOPS_TOOL_SRC = REPO_ROOT / "building-blocks" / "functions" / "devops-status-tool" / "src"
if str(DEVOPS_TOOL_SRC) not in sys.path:
    sys.path.append(str(DEVOPS_TOOL_SRC))

# Now we can import the tool safely from the flat 'src' directory
import tool  # noqa: E402

# Redact technical details in logs
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FoundryDevOpsAgentAdapter:
    """Adapter for the Azure AI Projects SDK with DevOps status tool integration."""

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
            logger.error("Failed to initialize AI Project Client.")
            raise RuntimeError("Could not connect to the Azure AI service.")

    def create_or_resolve_agent(self) -> Any:
        """Creates or resolves a Prompt Agent version with tools."""
        if not self._project_client:
            self.initialize_client()

        try:
            return self._project_client.agents.create_version(  # type: ignore
                agent_name=self.settings.agent_name,
                definition=PromptAgentDefinition(
                    model=self.settings.model_name,
                    instructions=SYSTEM_INSTRUCTIONS,
                    tools=get_tool_definitions(),
                ),
            )
        except Exception:
            logger.error("Failed to resolve agent.")
            raise RuntimeError("The agent service encountered an error.")

    def get_chat_response(self, user_input: str) -> str:
        """Invokes the agent and handles tool calls in a loop."""
        if not self._project_client:
            self.initialize_client()

        try:
            agent = self.create_or_resolve_agent()

            with self._project_client.get_openai_client() as openai_client:  # type: ignore
                conversation = openai_client.conversations.create()

                response = openai_client.responses.create(
                    input=user_input,
                    conversation=conversation.id,
                    extra_body={
                        "agent_reference": {
                            "name": agent.name,
                            "type": "agent_reference",
                        }
                    },
                )

                # Loop to handle function calls (max 5 iterations)
                for _ in range(5):
                    tool_calls = [
                        item for item in response.output if item.type == "function_call"
                    ]

                    if not tool_calls:
                        break

                    input_list: ResponseInputParam = []
                    for call in tool_calls:
                        if call.name == "get_build_status":
                            try:
                                # 1. Parse arguments from the agent
                                args = (
                                    json.loads(call.arguments) if call.arguments else {}
                                )

                                # 2. SAFETY: Enforce the configured scope from Settings.
                                # This solution is bounded to exactly one organization, project, and build.
                                # If the agent attempts to query a different scope, we reject it.
                                if (
                                    args.get("organization_url")
                                    != self.settings.organization_url
                                    or args.get("project") != self.settings.project
                                    or args.get("build_id") != self.settings.build_id
                                ):
                                    logger.warning("Agent attempted to query out-of-scope build.")
                                    input_list.append(
                                        FunctionCallOutput(
                                            type="function_call_output",
                                            call_id=call.call_id,
                                            output=json.dumps(
                                                {
                                                    "error": "The tool requested is unavailable for the specified scope."
                                                }
                                            ),
                                        )
                                    )
                                    continue

                                # 3. Execute the existing DevOps status tool
                                # It handles its own environment variables for PAT
                                result = tool.get_build_status_safe(args)

                                input_list.append(
                                    FunctionCallOutput(
                                        type="function_call_output",
                                        call_id=call.call_id,
                                        output=json.dumps(result),
                                    )
                                )
                            except Exception:
                                logger.error("DevOps tool execution failed.")
                                input_list.append(
                                    FunctionCallOutput(
                                        type="function_call_output",
                                        call_id=call.call_id,
                                        output=json.dumps(
                                            {
                                                "error": "The status tool encountered an error."
                                            }
                                        ),
                                    )
                                )
                        else:
                            logger.warning("Agent requested unknown tool.")
                            input_list.append(
                                FunctionCallOutput(
                                    type="function_call_output",
                                    call_id=call.call_id,
                                    output=json.dumps(
                                        {"error": "The tool requested is unavailable."}
                                    ),
                                )
                            )

                    response = openai_client.responses.create(
                        input=input_list,
                        conversation=conversation.id,
                        extra_body={
                            "agent_reference": {
                                "name": agent.name,
                                "type": "agent_reference",
                            }
                        },
                    )

                output_text = response.output_text
                if not output_text or not str(output_text).strip():
                    logger.error("Agent returned an empty response.")
                    raise RuntimeError("The agent was unable to provide a response.")

                return str(output_text)

        except RuntimeError:
            raise
        except Exception:
            logger.error("Error during response generation.")
            raise RuntimeError("The agent was unable to provide a response.")
