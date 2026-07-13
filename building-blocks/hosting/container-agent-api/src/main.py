import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, UTC

# Configure logging to be safe
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Container-hosted Agent API")


class AgentQueryRequest(BaseModel):
    """
    Request model for a bounded agent query.
    """

    model_config = ConfigDict(extra="forbid")

    query_type: str = Field(
        ...,
        description="The type of query to perform (e.g., 'status_summary')",
        pattern=r"^[a-zA-Z0-9_-]+$",
        max_length=32,
    )
    resource_id: str = Field(
        ...,
        description="The identifier of the resource to query",
        pattern=r"^[a-zA-Z0-9_-]+$",
        max_length=64,
    )


class AgentQueryResponse(BaseModel):
    """
    Customer-safe agent query response model.
    """

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="The current status of the resource")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    summary: str = Field(
        ..., description="A friendly business-level summary of the resource status"
    )


class ErrorResponse(BaseModel):
    """
    Safe error response model.
    """

    model_config = ConfigDict(extra="forbid")

    error_code: str = Field(..., description="A short, stable error code")
    friendly_message: str = Field(
        ..., description="A safe, human-readable error message"
    )


class HealthResponse(BaseModel):
    """
    Health check response model.
    """

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current server time")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to prevent technical leakage.
    """
    # Customer-Safe Logging Boundary:
    # Do NOT log the raw exception string or stack trace in a way that might be returned to the user.
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


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.
    """
    return HealthResponse(status="healthy", timestamp=datetime.now(UTC))


@app.post(
    "/agent/query",
    response_model=AgentQueryResponse,
    status_code=status.HTTP_200_OK,
    responses={500: {"model": ErrorResponse}},
)
async def agent_query(request: AgentQueryRequest):
    """
    Bounded read-only example endpoint.
    """
    # This is a stub implementation for the reference hosting block.
    # In a real scenario, this would call downstream services safely.
    # We avoid reflecting the resource_id to maintain a strict safe boundary.
    return AgentQueryResponse(
        status="active",
        summary="The requested resource is currently active and healthy. Technical details are redacted.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
