import logging
from typing import Annotated
from fastapi import FastAPI, Path, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict, StringConstraints
from datetime import datetime, UTC

# Configure logging to be safe
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Container-hosted Agent API")

# Narrow validation for identifiers to prevent injection and reflection
TaskId = Annotated[
    str, StringConstraints(pattern=r"^[a-zA-Z0-9_-]+$", min_length=1, max_length=64)
]


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_type: str = Field(
        ..., description="The type of agent request (e.g., 'summarize')"
    )
    payload: str = Field(
        ..., description="The content or context for the agent to process"
    )


class AgentStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="The current status of the agent task")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    summary: str = Field(..., description="A customer-safe summary of the progress")


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_code: str = Field(..., description="A short, stable error code")
    friendly_message: str = Field(
        ..., description="A safe, human-readable error message"
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Customer-Safe Logging Boundary:
    # Do NOT log the raw exception string or stack trace in a way that might be returned to the user.
    # We log a generic message and a correlation ID (if we had one) to the internal logs.
    logger.error(
        "An unexpected error occurred in the agent API. Technical details redacted."
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            friendly_message="An unexpected error occurred while processing the agent request.",
        ).model_dump(),
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}


@app.post(
    "/agent/request",
    response_model=AgentStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={500: {"model": ErrorResponse}},
)
async def create_agent_request(request: AgentRequest):
    # This is a stub implementation for the reference hosting block.
    # We return a 202 Accepted style response with a stable status.
    return AgentStatusResponse(
        status="accepted",
        summary="The agent request has been received and is queued for processing. Technical details are redacted.",
    )


@app.get(
    "/status/{task_id}",
    response_model=AgentStatusResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_status(
    task_id: Annotated[TaskId, Path(description="The unique identifier for the task")],
):
    # This is a stub implementation for the reference hosting block.
    # We explicitly avoid reflecting the task_id in the summary to maintain a safe boundary.
    return await handle_get_status(task_id)


async def handle_get_status(task_id: str):
    return AgentStatusResponse(
        status="running",
        summary="The requested agent task is currently being processed. Technical details are redacted.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
