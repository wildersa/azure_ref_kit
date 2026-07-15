import json
import logging
from typing import Any, Optional

try:
    import azure.ai.projects  # noqa: F401
    import azure.ai.projects.models  # noqa: F401
    import azure.identity  # noqa: F401
    import openai.types.responses.response_input_param  # noqa: F401
except ImportError:
    # Allow tests to run with mocks if SDK is not installed or for simple logic tests
    pass

from .config import Settings
from .agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions
from .tool_implementation import submit_task, get_task_status

logger = logging.getLogger(__name__)


class FoundryAgentAdapter:
    """Adapter for the Azure AI Projects SDK with asynchronous queue tool support."""

    def __init__(self, settings: Settings, project_client: Optional[Any] = None):
        self.settings = settings
        self._project_client = project_client

    def initialize_client(self) -> None:
        """Initializes the AIProjectClient using DefaultAzureCredential."""
        if self._project_client:
            return

        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

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
            from azure.ai.projects.models import PromptAgentDefinition

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
                # Create a conversation
                conversation = openai_client.conversations.create()

                # Initial request
                response = openai_client.responses.create(
                    input=user_input,
                    conversation=conversation.id,
                    extra_body={
                        "agent": {
                            "name": agent.name,
                            "type": "agent_reference",
                        }
                    },
                )

                # Loop to handle tool calls (max 5 iterations)
                for _ in range(5):
                    tool_calls = [
                        item for item in response.output if item.type == "function_call"
                    ]

                    if not tool_calls:
                        break

                    input_list = []
                    for call in tool_calls:
                        args = json.loads(call.arguments) if call.arguments else {}

                        if call.name == "submit_task":
                            result = submit_task(
                                operation_type=args.get("operation_type", ""),
                                parameters=args.get("parameters"),
                                settings=self.settings,
                            )
                        elif call.name == "get_task_status":
                            result = get_task_status(
                                correlation_id=args.get("correlation_id", ""),
                                settings=self.settings,
                            )
                        else:
                            logger.warning(f"Unknown tool requested: {call.name}")
                            result = {"error": "The tool requested is unavailable."}

                        try:
                            from openai.types.responses.response_input_param import (
                                FunctionCallOutput,
                            )

                            input_list.append(
                                FunctionCallOutput(
                                    type="function_call_output",
                                    call_id=call.call_id,
                                    output=json.dumps(result),
                                )
                            )
                        except ImportError:
                            # Fallback for mock-based tests
                            input_list.append(
                                {
                                    "type": "function_call_output",
                                    "call_id": call.call_id,
                                    "output": json.dumps(result),
                                }
                            )

                    # Submit tool outputs back to the agent
                    response = openai_client.responses.create(
                        input=input_list,
                        conversation=conversation.id,
                        extra_body={
                            "agent": {
                                "name": agent.name,
                                "type": "agent_reference",
                            }
                        },
                    )

                output_text = response.output_text
                if not output_text:
                    raise RuntimeError("The agent was unable to provide a response.")

                return str(output_text)

        except Exception as e:
            logger.error(f"Error during response generation: {str(e)}")
            raise RuntimeError("The agent was unable to provide a response.")
