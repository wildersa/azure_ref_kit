from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

# Correlation ID must be alphanumeric with hyphens, 8-64 chars.
CORRELATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9-]{8,64}$")


def is_valid_correlation_id(v: Any) -> bool:
    """Checks if a value is a valid correlation ID string."""
    if not isinstance(v, str):
        return False
    return bool(CORRELATION_ID_PATTERN.match(v))


class JobStatus(str, Enum):
    """
    Explicit business-level job status transitions.
    Aligned with CustomerSafeStatus schema and prompt requirements.
    """

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


def validate_parameters(v: dict[str, Any]) -> dict[str, Any]:
    """Ensures parameters are bounded in size and content."""
    if len(v) > 20:
        raise ValueError("Parameters dictionary exceeds maximum allowed items (20).")

    for key, value in v.items():
        if len(key) > 64:
            raise ValueError(
                f"Parameter key '{key[:10]}...' exceeds maximum length (64)."
            )
        if isinstance(value, str) and len(value) > 1024:
            raise ValueError(
                f"Parameter value for '{key}' exceeds maximum length (1024)."
            )
    return v


class SubmitRequest(BaseModel):
    """Request model for submitting a new job."""

    model_config = ConfigDict(extra="forbid")

    operation_type: str = Field(
        ...,
        description="The type of operation to perform.",
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9_]+$",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Operation-specific parameters."
    )

    @field_validator("parameters")
    @classmethod
    def check_parameters(cls, v: dict[str, Any]) -> dict[str, Any]:
        return validate_parameters(v)


class SubmitResponse(BaseModel):
    """Response model after successfully enqueuing a job."""

    model_config = ConfigDict(extra="forbid")

    correlation_id: str = Field(
        ..., description="The opaque correlation ID for the job."
    )
    status: JobStatus = Field(JobStatus.QUEUED, description="Initial job status.")


class JobInput(BaseModel):
    """
    Validated input for the queue job (internal message schema).
    """

    model_config = ConfigDict(extra="forbid")

    correlation_id: str = Field(
        ...,
        description="Unique identifier for the job, used to link results to requests.",
        min_length=8,
        max_length=64,
    )
    operation_type: str = Field(
        ...,
        description="The type of operation to perform.",
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9_]+$",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Operation-specific parameters."
    )

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, v: str) -> str:
        if not CORRELATION_ID_PATTERN.match(v):
            raise ValueError(
                "Correlation ID must be alphanumeric with hyphens, 8-64 characters."
            )
        return v

    @field_validator("parameters")
    @classmethod
    def check_parameters(cls, v: dict[str, Any]) -> dict[str, Any]:
        return validate_parameters(v)


class JobResult(BaseModel):
    """
    Customer-safe job result record (internal storage and result queue schema).
    """

    model_config = ConfigDict(extra="forbid")

    correlation_id: str = Field(..., description="The original correlation ID.")
    status: JobStatus = Field(..., description="The final status of the job.")
    result_data: Optional[dict[str, Any]] = Field(
        None, description="Successful operation results."
    )
    friendly_error: Optional[str] = Field(
        None, description="Customer-safe error message if failed."
    )
    timestamp: str = Field(..., description="ISO 8601 timestamp of completion.")

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, v: str) -> str:
        if not CORRELATION_ID_PATTERN.match(v):
            raise ValueError("Invalid Correlation ID format.")
        return v


class JobStatusResponse(BaseModel):
    """
    Customer-safe status response (API surface).
    Aligned with building-blocks/security/customer-safe-status-boundary and shared contracts.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="The opaque correlation ID.")
    status: JobStatus = Field(..., description="The current status.")
    business_summary: Optional[str] = Field(
        None, description="Safe summary of progress.", max_length=1000
    )
    created_at: str = Field(..., description="ISO 8601 creation timestamp.")
    started_at: Optional[str] = Field(None, description="ISO 8601 start timestamp.")
    finished_at: Optional[str] = Field(None, description="ISO 8601 finish timestamp.")
    result_data: Optional[dict[str, Any]] = Field(
        None, description="Operation results."
    )
    friendly_error: Optional[str] = Field(
        None, description="Safe error message.", max_length=1000
    )
