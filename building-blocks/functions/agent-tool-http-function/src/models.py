from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class SystemStatusResponse(BaseModel):
    """
    Deterministic response model for the system status tool.
    Ensures a safe, read-only boundary for AI agents.
    """

    model_config = ConfigDict(extra="forbid")

    business_status: str = Field(
        ...,
        description="Friendly operational status (e.g., 'operational', 'degraded').",
    )
    service_health: str = Field(
        ..., description="Technical health indicator (e.g., 'healthy', 'unhealthy')."
    )
    active_regions: List[str] = Field(
        ..., description="List of regions currently serving traffic."
    )
    last_updated: datetime = Field(
        ..., description="ISO8601 timestamp of the last status update."
    )
    environment: str = Field(
        ..., description="Name of the environment (e.g., 'production', 'staging')."
    )


class ErrorResponse(BaseModel):
    """
    Customer-safe error response model.
    """

    model_config = ConfigDict(extra="forbid")

    error_code: str = Field(..., description="Machine-readable error code.")
    friendly_message: str = Field(
        ..., description="Human-readable message safe for customer exposure."
    )
