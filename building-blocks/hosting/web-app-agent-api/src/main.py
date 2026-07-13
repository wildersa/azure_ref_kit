import logging
import os
from datetime import datetime, UTC
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

# Configure logging to be safe - do not log PII or secrets
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Web App Hosted Agent API",
    description="Minimal bounded agent-facing API reference for Azure App Service.",
    version="1.0.0",
)


class AgentQueryRequest(BaseModel):
    """
    Strict input model for agent queries.
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
    Customer-safe output model for agent queries.
    """

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="The current status of the resource")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    summary: str = Field(
        ..., description="A friendly business-level summary of the resource status"
    )


class ErrorResponse(BaseModel):
    """
    Safe error response model to prevent technical leakage.
    """

    model_config = ConfigDict(extra="forbid")

    error_code: str = Field(..., description="A short, stable error code")
    friendly_message: str = Field(
        ..., description="A safe, human-readable error message"
    )


class HealthResponse(BaseModel):
    """
    Service health response model.
    """

    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current server time")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that redacts technical details.
    """
    # Log the fact that an error occurred, but avoid leaking internal state in the log message if it might be exposed.
    # In a real app, you might log a correlation ID here.
    logger.error("An unexpected error occurred. Technical details are redacted.")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error_code="INTERNAL_ERROR",
            friendly_message="An unexpected error occurred while processing your request.",
        ).model_dump(),
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint for Azure App Service.
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
    Bounded read-only query endpoint.
    """
    # Implementation Note: This is a reference stub.
    # A real implementation would call downstream services safely using Managed Identity.
    if request.resource_id == "trigger-error":
        raise ValueError("Triggered internal error for testing")

    return AgentQueryResponse(
        status="active",
        summary="The resource is currently operating within normal parameters. Technical details redacted.",
    )


if __name__ == "__main__":
    import uvicorn

    # App Service for Containers typically sets WEBSITES_PORT
    # Locally or in other environments, PORT is standard
    port = int(os.environ.get("WEBSITES_PORT", os.environ.get("PORT", 8080)))
    uvicorn.run(app, host="0.0.0.0", port=port)
