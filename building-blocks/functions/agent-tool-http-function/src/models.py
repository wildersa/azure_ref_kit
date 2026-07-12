from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ResourceType(str, Enum):
    """Supported resource types for the tool."""

    VIRTUAL_MACHINE = "virtual_machine"
    STORAGE_ACCOUNT = "storage_account"
    DATABASE = "database"


class ResourceStatus(str, Enum):
    """Resource status enum."""

    RUNNING = "running"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ResourceInfoRequest(BaseModel):
    """Request model for retrieving resource information."""

    model_config = ConfigDict(extra="forbid")

    resource_id: str = Field(
        ...,
        description="The unique identifier for the resource.",
        min_length=1,
        max_length=128,
    )
    resource_type: ResourceType = Field(..., description="The type of the resource.")


class ResourceInfoResponse(BaseModel):
    """
    Customer-safe resource info response model.
    """

    model_config = ConfigDict(extra="forbid")

    resource_id: str = Field(..., description="The unique identifier for the resource.")
    resource_type: ResourceType = Field(..., description="The type of the resource.")
    status: ResourceStatus = Field(
        ..., description="The current status of the resource."
    )
    location: str = Field(
        ..., description="The Azure region where the resource is located."
    )
    tags: dict[str, str] = Field(
        default_factory=dict, description="Tags associated with the resource."
    )
    summary: str = Field(
        ..., description="A friendly business-level summary of the resource status."
    )
