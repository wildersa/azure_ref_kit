from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, StringConstraints
from typing_extensions import Annotated

# Regex for safe identifiers: alphanumeric, hyphens, underscores, dots, and spaces.
# No leading/trailing spaces. No path separators or control characters.
SAFE_ID_PATTERN = r"^[a-zA-Z0-9_\-\. ]+$"
SafeId = Annotated[
    str, StringConstraints(pattern=SAFE_ID_PATTERN, min_length=1, max_length=128)
]

# Pattern for friendly summaries: permits standard characters and common punctuation.
SUMMARY_PATTERN = r"^[a-zA-Z0-9_\-\. \(\)\',;!]+$"
SafeSummary = Annotated[
    str, StringConstraints(pattern=SUMMARY_PATTERN, min_length=1, max_length=512)
]

# Short SHA pattern: exactly 7 or 8 hex characters.
SHA_PATTERN = r"^[a-fA-F0-9]{7,8}$"
SafeSha = Annotated[
    str, StringConstraints(pattern=SHA_PATTERN, min_length=7, max_length=8)
]


class PipelineStatus(str, Enum):
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    QUEUED = "queued"
    CANCELLING = "cancelling"
    POSTPONED = "postponed"
    NOT_STARTED = "notStarted"


class PipelineResult(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    PARTIALLY_SUCCEEDED = "partiallySucceeded"
    NONE = "none"


class GetPipelineRunStatusRequest(BaseModel):
    """Request to get the status of a specific pipeline run."""

    model_config = ConfigDict(extra="forbid")

    pipeline_id: SafeId = Field(..., description="The ID or name of the pipeline.")
    run_id: SafeId = Field(..., description="The specific run ID to query.")


class GetPipelineRunStatusResponse(BaseModel):
    """Response containing the status and summary of a pipeline run."""

    model_config = ConfigDict(extra="forbid")

    pipeline_name: SafeId = Field(
        ..., description="The name of the Azure DevOps pipeline."
    )
    run_id: SafeId = Field(..., description="The unique identifier for the specific run.")
    status: PipelineStatus = Field(..., description="The current state of the run.")
    result: PipelineResult = Field(..., description="The outcome of a completed run.")
    branch: SafeId = Field(..., description="The source branch for the run.")
    commit_sha: Optional[SafeSha] = Field(
        None, description="The short commit SHA associated with the run."
    )
    start_time: datetime = Field(..., description="When the run started (ISO 8601).")
    end_time: Optional[datetime] = Field(
        None, description="When the run finished (ISO 8601)."
    )
    duration_seconds: Optional[Annotated[int, Field(ge=0, le=864000)]] = Field(
        None, description="The total duration of the run in seconds (up to 10 days)."
    )
    summary: Optional[SafeSummary] = Field(
        None, description="A friendly business-level summary of the run status."
    )
