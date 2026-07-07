"""
Minimal example showing how to initialize the DevOps Status Agent.
This follows the Azure AI Projects SDK pattern for Prompt Agents.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from .agent_definition import SYSTEM_INSTRUCTIONS, get_tool_definitions

def main():
    # Load configuration from environment variables
    # Expected: https://<resource-name>.ai.azure.com/api/projects/<project-name>
    project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    model_deployment = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")

    if not project_endpoint:
        print("AZURE_AI_PROJECT_ENDPOINT is not set. Skipping real initialization.")
        return

    # Initialize the project client
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    # Create the agent version
    # In a real scenario, you might check if an agent with this name already exists.
    agent = project_client.agents.create_version(
        agent_name="devops-status-agent",
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions=SYSTEM_INSTRUCTIONS,
            tools=get_tool_definitions(),
        ),
    )

    print(f"Agent '{agent.name}' created with version '{agent.version}'.")
    print(f"Agent instructions: {agent.definition.instructions[:100]}...")
    print(f"Tool count: {len(agent.definition.tools)}")

    # Example of how to handle tool calls in your application loop
    # response = openai.responses.create(...)
    # for item in response.output:
    #     if item.type == "function_call":
    #         # Resolve tool call via your DevOps Status integration
    #         pass

if __name__ == "__main__":
    main()
