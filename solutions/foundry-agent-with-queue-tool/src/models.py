from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SubmitResponse(BaseModel):
    """Bounded response for task submission."""

    model_config = ConfigDict(extra="forbid")

    correlation_id: str = Field(
        ..., description="The opaque correlation ID for the task."
    )
    status: JobStatus = Field(..., description="The initial status of the task.")


class TaskStatusResponse(BaseModel):
    """Bounded response for task status lookup."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="The opaque correlation ID.")
    status: JobStatus = Field(..., description="The current status.")
    business_summary: Optional[str] = Field(
        None, description="Safe summary of progress."
    )
    result_data: Optional[Dict[str, Any]] = Field(
        None, description="Operation results."
    )
    error_message: Optional[str] = Field(None, description="Safe error message.")
