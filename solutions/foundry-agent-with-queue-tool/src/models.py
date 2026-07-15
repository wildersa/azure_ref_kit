from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Shared bounds for safety
MAX_ID_LENGTH = 64
MAX_SUMMARY_LENGTH = 256
MAX_ERROR_LENGTH = 256
MAX_RESULT_KEYS = 10
MAX_RESULT_VALUE_LENGTH = 1024


class SubmitResponse(BaseModel):
    """Bounded response for task submission."""

    model_config = ConfigDict(extra="forbid")

    correlation_id: str = Field(
        ...,
        description="The opaque correlation ID for the task.",
        min_length=8,
        max_length=MAX_ID_LENGTH,
    )
    status: JobStatus = Field(..., description="The initial status of the task.")


class TaskStatusResponse(BaseModel):
    """Bounded response for task status lookup."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        description="The opaque correlation ID.",
        min_length=8,
        max_length=MAX_ID_LENGTH,
    )
    status: JobStatus = Field(..., description="The current status.")
    business_summary: Optional[str] = Field(
        None,
        description="Safe summary of progress.",
        max_length=MAX_SUMMARY_LENGTH,
    )
    result_data: Optional[Dict[str, Any]] = Field(
        None, description="Operation results."
    )
    error_message: Optional[str] = Field(
        None,
        description="Safe error message.",
        max_length=MAX_ERROR_LENGTH,
    )

    @field_validator("result_data")
    @classmethod
    def validate_result_data(
        cls, v: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        if v is None:
            return v

        if len(v) > MAX_RESULT_KEYS:
            raise ValueError(
                f"Result data contains too many keys (max {MAX_RESULT_KEYS})."
            )

        for key, val in v.items():
            if len(key) > 64:
                raise ValueError("Result key too long.")

            # For simplicity in this reference, we check stringified length of values
            val_str = str(val)
            if len(val_str) > MAX_RESULT_VALUE_LENGTH:
                raise ValueError(f"Result value for key '{key}' is too large.")

        return v
