from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


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

    pipeline_id: str = Field(..., description="The ID or name of the pipeline.")
    run_id: str = Field(..., description="The specific run ID to query.")


class GetPipelineRunStatusResponse(BaseModel):
    """Response containing the status and summary of a pipeline run."""

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


class GetLatestBuildSummaryRequest(BaseModel):
    """Request to get the summary of the latest build."""

    pipeline_id: str = Field(..., description="The ID or name of the pipeline.")
    branch: Optional[str] = Field(
        None, description="Filter by branch name (defaults to default branch)."
    )


class GetLatestBuildSummaryResponse(BaseModel):
    """Response containing the summary of the most recent build."""

    pipeline_name: str = Field(..., description="The name of the pipeline.")
    build_number: str = Field(..., description="The build number (e.g., 20240102.1).")
    status: str = Field(..., description="The current state of the build.")
    result: str = Field(..., description="The outcome of a completed build.")
    branch: str = Field(..., description="The source branch for the build.")
    finish_time: datetime = Field(
        ..., description="When the build finished (ISO 8601)."
    )
    summary: Optional[str] = Field(
        None, description="A friendly business-level summary of the build status."
    )
    portal_url: HttpUrl = Field(
        ..., description="A sanitized link to the build in the Azure DevOps portal."
    )
