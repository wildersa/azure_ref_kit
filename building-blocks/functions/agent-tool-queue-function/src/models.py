from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re
import json

# Correlation ID must be alphanumeric with hyphens, 8-64 chars.
CORRELATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9-]{8,64}$")

# Payload boundaries
MAX_PAYLOAD_SIZE_BYTES = 10 * 1024  # 10KB
MAX_RECURSIVE_DEPTH = 3
MAX_TOTAL_ITEMS = 50


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


def validate_bounded_payload(
    v: Any, depth: int = 0, item_count: int = 0, label: str = "payload"
) -> int:
    """
    Recursively validates depth and item count of a JSON-serializable payload.
    Returns the total item count.
    """
    if depth > MAX_RECURSIVE_DEPTH:
        raise ValueError(
            f"{label} exceeds maximum recursive depth ({MAX_RECURSIVE_DEPTH})."
        )

    current_count = item_count + 1
    if current_count > MAX_TOTAL_ITEMS:
        raise ValueError(f"{label} exceeds maximum total items ({MAX_TOTAL_ITEMS}).")

    if isinstance(v, dict):
        for key, value in v.items():
            if len(str(key)) > 64:
                raise ValueError(
                    f"{label} key '{str(key)[:10]}...' exceeds maximum length (64)."
                )
            current_count = validate_bounded_payload(
                value, depth + 1, current_count, label
            )
    elif isinstance(v, list):
        for item in v:
            current_count = validate_bounded_payload(
                item, depth + 1, current_count, label
            )
    elif isinstance(v, str):
        if len(v) > 1024:
            raise ValueError(f"{label} string value exceeds maximum length (1024).")

    return current_count


def validate_parameters(v: dict[str, Any]) -> dict[str, Any]:
    """Ensures parameters are bounded in size, depth, and content."""
    # 1. Check total serialized size
    try:
        serialized = json.dumps(v)
        if len(serialized) > MAX_PAYLOAD_SIZE_BYTES:
            raise ValueError(
                f"Parameters exceed maximum serialized size ({MAX_PAYLOAD_SIZE_BYTES} bytes)."
            )
    except (TypeError, ValueError) as e:
        if isinstance(e, ValueError) and "maximum serialized size" in str(e):
            raise
        raise ValueError("Parameters must be JSON-serializable.")

    # 2. Recursive depth and item count validation
    validate_bounded_payload(v, label="Parameters")

    return v


def validate_result_data(v: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Ensures result data is bounded before persistence or exposure."""
    if v is None:
        return v

    try:
        serialized = json.dumps(v)
        if len(serialized) > MAX_PAYLOAD_SIZE_BYTES:
            raise ValueError(
                f"Result data exceeds maximum serialized size ({MAX_PAYLOAD_SIZE_BYTES} bytes)."
            )
    except (TypeError, ValueError) as e:
        if isinstance(e, ValueError) and "maximum serialized size" in str(e):
            raise
        raise ValueError("Result data must be JSON-serializable.")

    validate_bounded_payload(v, label="Result data")
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

    @field_validator("result_data")
    @classmethod
    def check_result_data(cls, v: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        return validate_result_data(v)


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

    @field_validator("result_data")
    @classmethod
    def check_result_data(cls, v: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        return validate_result_data(v)
