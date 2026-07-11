import json
import logging
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
from .tool_implementation import get_system_status, validate_tool_arguments

# Redact technical details in logs
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FoundryAgentAdapter:
    """Adapter for the Azure AI Projects SDK with controlled tool execution."""

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
            # We assume self._project_client is initialized here
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
                # Create a conversation for multi-turn interaction
                conversation = openai_client.conversations.create()

                # Initial request
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

                # Loop to handle function calls (max 5 iterations to prevent infinite loops)
                for _ in range(5):
                    # Filter output for function calls
                    tool_calls = [
                        item for item in response.output if item.type == "function_call"
                    ]

                    if not tool_calls:
                        break

                    input_list: ResponseInputParam = []
                    for call in tool_calls:
                        if call.name == "get_system_status":
                            try:
                                # Validate arguments
                                args = (
                                    json.loads(call.arguments) if call.arguments else {}
                                )
                                validate_tool_arguments(args)

                                # Execute tool safely
                                result = get_system_status()

                                input_list.append(
                                    FunctionCallOutput(
                                        type="function_call_output",
                                        call_id=call.call_id,
                                        output=json.dumps(result),
                                    )
                                )
                            except Exception as e:
                                logger.error(f"Tool execution failed: {e}")
                                # Provide a sanitized error back to the agent
                                input_list.append(
                                    FunctionCallOutput(
                                        type="function_call_output",
                                        call_id=call.call_id,
                                        output=json.dumps(
                                            {"error": "The tool encountered an error."}
                                        ),
                                    )
                                )
                        else:
                            logger.warning(f"Agent requested unknown tool: {call.name}")
                            input_list.append(
                                FunctionCallOutput(
                                    type="function_call_output",
                                    call_id=call.call_id,
                                    output=json.dumps(
                                        {"error": f"Unknown tool: {call.name}"}
                                    ),
                                )
                            )

                    # Submit tool outputs back to the agent
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
                    logger.error("Agent returned an empty or missing response.")
                    raise RuntimeError("The agent was unable to provide a response.")

                return str(output_text)

        except RuntimeError:
            # Re-raise sanitized errors
            raise
        except Exception:
            logger.error("Error during response generation.")
            # Sanitize failures: do not return stack traces or raw provider payloads
            raise RuntimeError("The agent was unable to provide a response.")
