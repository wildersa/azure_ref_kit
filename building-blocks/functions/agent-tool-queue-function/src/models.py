from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

# Correlation ID must be alphanumeric with hyphens, 8-64 chars.
CORRELATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9-]{8,64}$")


class JobStatus(str, Enum):
    """Explicit job status transitions."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobInput(BaseModel):
    """
    Validated input for the queue job.
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
        max_length=32,
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


class JobResult(BaseModel):
    """
    Customer-safe job result record.
    """

    model_config = ConfigDict(extra="forbid")

    correlation_id: str = Field(..., description="The original correlation ID.")
    status: JobStatus = Field(..., description="The final status of the job.")
    result_data: Optional[dict[str, Any]] = Field(
        None, description="Successful operation results."
    )
    error_message: Optional[str] = Field(
        None, description="Customer-safe error message if failed."
    )
    timestamp: str = Field(..., description="ISO 8601 timestamp of completion.")

    @field_validator("correlation_id")
    @classmethod
    def validate_correlation_id(cls, v: str) -> str:
        if not CORRELATION_ID_PATTERN.match(v):
            raise ValueError("Invalid Correlation ID format.")
        return v
