import logging
from typing import Any, Optional

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential

from .config import Settings

# Redact technical details in logs
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FoundryAgentAdapter:
    """Adapter for the Azure AI Projects SDK to interact with Foundry Agents via APIM Gateway."""

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
            # Redact technical details like endpoint or credentials in the exception message
            logger.error("Failed to initialize AI Project Client.")
            raise RuntimeError("Could not connect to the Azure AI service.")

    def create_or_resolve_agent(self) -> Any:
        """Creates or resolves a Prompt Agent version."""
        if not self._project_client:
            self.initialize_client()

        try:
            # We build the qualified model string to route through the APIM gateway connection
            # Format: <connection-name>/<deployment-name>
            qualified_model = (
                f"{self.settings.gateway_connection_name}/{self.settings.model_name}"
            )

            # We assume self._project_client is initialized here
            return self._project_client.agents.create_version(  # type: ignore
                agent_name=self.settings.agent_name,
                definition=PromptAgentDefinition(
                    model=qualified_model,
                    instructions="You are a helpful assistant.",
                ),
            )
        except Exception:
            # Do NOT log the agent name on failure as it is an Azure resource identifier
            logger.error("Failed to resolve agent.")
            raise RuntimeError("The agent service encountered an error.")

    def get_chat_response(self, user_input: str) -> str:
        """Invokes the agent through the Responses API and returns the output text."""
        if not self._project_client:
            self.initialize_client()

        try:
            agent = self.create_or_resolve_agent()
            openai_client = self._project_client.get_openai_client()  # type: ignore

            response = openai_client.responses.create(
                input=user_input,
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
        except Exception as e:
            # Check for 429 Too Many Requests (Rate Limit) from the gateway
            if "429" in str(e) or "too many requests" in str(e).lower():
                logger.warning("Agent request was rate limited by the AI Gateway.")
                raise RuntimeError(
                    "The agent is currently busy due to high demand. Please try again in a moment."
                )

            logger.error("Error during response generation.")
            # Sanitize failures: do not return stack traces or raw provider payloads
            raise RuntimeError("The agent was unable to provide a response.")
