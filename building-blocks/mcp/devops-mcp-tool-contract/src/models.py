from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, StringConstraints
from typing_extensions import Annotated

# Regex for safe identifiers: alphanumeric, hyphens, underscores, dots, and spaces.
# No leading/trailing spaces. No path separators or control characters.
SAFE_ID_PATTERN = r"^[a-zA-Z0-9_\-\. ]+$"
SafeId = Annotated[
    str, StringConstraints(pattern=SAFE_ID_PATTERN, min_length=1, max_length=128)
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

    pipeline_name: str = Field(
        ..., description="The name of the Azure DevOps pipeline."
    )
    run_id: str = Field(..., description="The unique identifier for the specific run.")
    status: PipelineStatus = Field(..., description="The current state of the run.")
    result: PipelineResult = Field(..., description="The outcome of a completed run.")
    branch: str = Field(..., description="The source branch for the run.")
    commit_sha: Optional[str] = Field(
        None, description="The short commit SHA associated with the run."
    )
    start_time: datetime = Field(..., description="When the run started (ISO 8601).")
    end_time: Optional[datetime] = Field(
        None, description="When the run finished (ISO 8601)."
    )
    duration_seconds: Optional[int] = Field(
        None, description="The total duration of the run in seconds."
    )
    summary: Optional[str] = Field(
        None, description="A friendly business-level summary of the run status."
    )
    portal_url: HttpUrl = Field(
        ..., description="A sanitized link to the run in the Azure DevOps portal."
    )


class ListRecentPipelineRunsRequest(BaseModel):
    """Request to list recent runs of a specific pipeline."""

    model_config = ConfigDict(extra="forbid")

    pipeline_id: SafeId = Field(..., description="The ID or name of the pipeline.")
    branch: Optional[SafeId] = Field(
        None, description="Filter by branch name (defaults to all branches)."
    )
    top: Annotated[int, Field(ge=1, le=20)] = Field(
        5, description="Number of recent runs to return (default: 5, max: 20)."
    )


class PipelineRunSummary(BaseModel):
    """Brief summary of a single pipeline run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="The unique identifier for the specific run.")
    status: PipelineStatus = Field(..., description="The current state of the run.")
    result: PipelineResult = Field(..., description="The outcome of a completed run.")
    branch: str = Field(..., description="The source branch for the run.")
    start_time: datetime = Field(..., description="When the run started (ISO 8601).")


class ListRecentPipelineRunsResponse(BaseModel):
    """Response containing a list of recent pipeline runs."""

    model_config = ConfigDict(extra="forbid")

    pipeline_name: str = Field(
        ..., description="The name of the Azure DevOps pipeline."
    )
    runs: list[PipelineRunSummary] = Field(..., description="List of recent runs.")
