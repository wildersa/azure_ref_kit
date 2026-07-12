from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, HttpUrl


class BuildStatus(str, Enum):
    """Azure DevOps Build Status enum."""

    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    QUEUED = "queued"
    CANCELLING = "cancelling"
    POSTPONED = "postponed"
    NOT_STARTED = "notStarted"
    NONE = "none"
    ALL = "all"


class BuildResult(str, Enum):
    """Azure DevOps Build Result enum."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    PARTIALLY_SUCCEEDED = "partiallySucceeded"
    NONE = "none"


class DevOpsStatusRequest(BaseModel):
    """Request model for retrieving Azure DevOps build status."""

    model_config = ConfigDict(extra="forbid")

    organization_url: HttpUrl = Field(
        ..., description="The URL of the Azure DevOps organization."
    )
    project: str = Field(..., description="The project name or ID.")
    build_id: int = Field(..., description="The unique identifier for the build.")


class DevOpsStatusResponse(BaseModel):
    """
    Customer-safe DevOps status response model.
    Matches shared/contracts/devops-status.schema.json.
    """

    model_config = ConfigDict(extra="forbid")

    pipeline_name: str = Field(
        ..., description="The name of the Azure DevOps pipeline."
    )
    run_id: str = Field(
        ..., description="The unique identifier for the specific run or build."
    )
    status: BuildStatus = Field(..., description="The current state of the run.")
    result: BuildResult = Field(..., description="The outcome of a completed run.")
    branch: str = Field(
        "redacted", description="The source branch (redacted for safety)."
    )
    queue_time: Optional[datetime] = Field(None, description="When the run was queued.")
    start_time: Optional[datetime] = Field(None, description="When the run started.")
    end_time: Optional[datetime] = Field(None, description="When the run finished.")
    duration_seconds: Optional[int] = Field(
        None, description="The total duration of the run in seconds."
    )
    summary: Optional[str] = Field(
        None, description="A friendly business-level summary of the run status."
    )
    portal_url: HttpUrl = Field(
        ..., description="A sanitized link to the run in the Azure DevOps portal."
    )
