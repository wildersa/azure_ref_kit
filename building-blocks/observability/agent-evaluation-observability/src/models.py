from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, StringConstraints
from typing_extensions import Annotated

# Regex for safe identifiers: alphanumeric, hyphens, underscores, dots, and spaces.
SAFE_ID_PATTERN = r"^[a-zA-Z0-9_\-\. ]+$"
SafeId = Annotated[
    str, StringConstraints(pattern=SAFE_ID_PATTERN, min_length=1, max_length=128)
]


class OperationType(str, Enum):
    AGENT_TURN = "agent_turn"
    TOOL_CALL = "tool_call"
    REASONING_STEP = "reasoning_step"
    SAFETY_CHECK = "safety_check"


class ToolName(str, Enum):
    GET_PIPELINE_STATUS = "get_pipeline_status"
    LIST_ARTIFACTS = "list_artifacts"
    GET_BUILD_LOG_SUMMARY = "get_build_log_summary"
    UNAUTHORIZED_TOOL = "[UNAUTHORIZED_TOOL]"


class TraceStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    REFUSAL = "refusal"
    ERROR = "error"


class ErrorCategory(str, Enum):
    RATE_LIMIT = "rate_limit"
    TOOL_TIMEOUT = "tool_timeout"
    AUTHENTICATION_FAILURE = "authentication_failure"
    POLICY_VIOLATION = "policy_violation"
    UPSTREAM_ERROR = "upstream_error"
    VALIDATION_ERROR = "validation_error"


class SafeTraceEvent(BaseModel):
    """Deterministic contract for customer-safe agent technical telemetry."""

    model_config = ConfigDict(extra="forbid")

    request_id: SafeId = Field(
        ..., description="Correlation ID for the end-to-end request."
    )
    agent_id: Optional[SafeId] = Field(
        None, description="Identifier for the agent version."
    )
    operation_type: OperationType = Field(
        ..., description="The category of the operation being traced."
    )
    tool_name: Optional[ToolName] = Field(
        None, description="Controlled allowlist of tool names."
    )
    status: TraceStatus = Field(..., description="High-level outcome category.")
    duration_ms: Annotated[int, Field(ge=0, le=3600000)] = Field(
        ..., description="Latency of the operation in milliseconds."
    )
    error_category: Optional[ErrorCategory] = Field(
        None, description="Controlled enum for friendly error categories."
    )
    correlation_id: Optional[SafeId] = Field(
        None, description="Optional secondary correlation ID."
    )


class EvaluationMetrics(BaseModel):
    """Metrics for agent evaluation."""

    model_config = ConfigDict(extra="forbid")

    task_completion: bool = Field(
        ..., description="True if the agent successfully completed the requested task."
    )
    safe_tool_use: bool = Field(
        ...,
        description="True if the agent called tools correctly and within permitted boundaries.",
    )
    groundedness_score: Annotated[float, Field(ge=0, le=5)] = Field(
        ..., description="Score indicating how well the response is grounded."
    )
    safe_failure_behavior: bool = Field(
        ...,
        description="True if failures resulted in friendly, non-technical messages.",
    )
    latency_ms: Optional[Annotated[int, Field(ge=0, le=3600000)]] = Field(
        None, description="Total end-to-end latency for the evaluated turn."
    )
    estimated_cost_usd: Optional[Annotated[float, Field(ge=0, le=10.0)]] = Field(
        None, description="Estimated cost of the turn in USD."
    )


class EvaluationStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    NEEDS_REVIEW = "needs_review"


class SafeEvaluationResult(BaseModel):
    """Deterministic contract for customer-safe agent evaluation outcomes."""

    model_config = ConfigDict(extra="forbid")

    evaluation_id: SafeId = Field(
        ..., description="Unique identifier for the evaluation run."
    )
    request_id: SafeId = Field(
        ..., description="Correlation ID for the specific request being evaluated."
    )
    metrics: EvaluationMetrics = Field(..., description="Metrics for the evaluation.")
    status: EvaluationStatus = Field(
        ..., description="Overall deterministic evaluation outcome."
    )
