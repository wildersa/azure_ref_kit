"""
Mock objects for Azure AI Projects SDK to support local validation.
"""

from typing import List, Any
from dataclasses import dataclass


@dataclass
class Agent:
    name: str


class Conversations:
    def create(self):
        return type("obj", (object,), {"id": "mock-conv-id"})


class OutputItem:
    def __init__(self, type: str, **kwargs):
        self.type = type
        for k, v in kwargs.items():
            setattr(self, k, v)


class Response:
    def __init__(self, id: str, output: List[OutputItem], output_text: str = ""):
        self.id = id
        self.output = output
        self.output_text = output_text


class ResponseClient:
    def __init__(self, create_func):
        self.create = create_func


class OpenAIClient:
    def __init__(self):
        self.conversations = Conversations()
        self.responses = ResponseClient(self.create_response)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def create_response(self, input: Any, **kwargs):
        # Logic to simulate tool calls or final response
        # When agent receives "submit", it should trigger a function call
        if isinstance(input, str) and "submit" in input.lower():
            return Response(
                "res-1",
                [
                    OutputItem(
                        "function_call",
                        name="submit_task",
                        arguments='{"operation_type": "ping"}',
                        call_id="call-1",
                    )
                ],
            )
        # When agent receives function call output, it should return final text
        elif isinstance(input, list) and len(input) > 0:
            item = input[0]
            # Handle both object and dict
            item_type = getattr(item, "type", None) or (
                item.get("type") if isinstance(item, dict) else None
            )
            if item_type == "function_call_output":
                return Response(
                    "res-2", [], "Your task has been submitted. Correlation ID: mock-id"
                )

        return Response("res-def", [], "I am a mock agent.")


class Agents:
    def create_version(self, agent_name: str, definition: Any):
        return Agent(name=agent_name)


class AIProjectClient:
    def __init__(self, endpoint: str, credential: Any):
        self.endpoint = endpoint
        self.agents = Agents()

    def get_openai_client(self):
        return OpenAIClient()
