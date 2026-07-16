from enum import Enum
from typing import Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, StringConstraints
from typing_extensions import Annotated

# Regex for safe identifiers: alphanumeric, hyphens, underscores, dots, and spaces.
# Also allows brackets [] for redaction placeholders and = for key=value pairs.
SAFE_ID_PATTERN = r"^[a-zA-Z0-9_\-\. \[\]\=]+$"

# Strict length bounds for different telemetry fields
SafeId = Annotated[
    str, StringConstraints(pattern=SAFE_ID_PATTERN, min_length=1, max_length=128)
]
SafeKey = Annotated[
    str, StringConstraints(pattern=SAFE_ID_PATTERN, min_length=1, max_length=64)
]
SafeValue = Annotated[
    str, StringConstraints(pattern=SAFE_ID_PATTERN, min_length=1, max_length=512)
]


class OperationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ERROR = "ERROR"


class TechnicalTelemetry(BaseModel):
    """
    Strict contract for technical telemetry attributes.
    This ensures only safe, non-sensitive metadata is sent to Application Insights.
    """

    model_config = ConfigDict(extra="forbid")

    operation_name: SafeId = Field(
        ..., description="Name of the operation being traced."
    )
    operation_status: OperationStatus = Field(
        ..., description="High-level outcome of the operation."
    )
    duration_ms: Annotated[int, Field(ge=0, le=3600000)] = Field(
        ..., description="Latency of the operation in milliseconds."
    )
    request_id: Optional[SafeId] = Field(
        None, description="Correlation ID for the request."
    )
    component_name: Optional[SafeId] = Field(
        None, description="Name of the component emitting telemetry."
    )
    target_resource: Optional[SafeId] = Field(
        None, description="Name of the target resource or dependency."
    )

    # Custom dimensions are limited to 20 entries with strict key/value length bounds
    custom_dimensions: Optional[
        Annotated[Dict[SafeKey, SafeValue], Field(max_length=20)]
    ] = Field(
        None, description="Controlled key-value pairs for additional safe metadata."
    )
