import sys
import pytest
from pathlib import Path
from pydantic import ValidationError

# Add building blocks to sys.path
REPO_ROOT = Path(__file__).parent.parent.parent.parent
OBS_SRC = (
    REPO_ROOT
    / "building-blocks"
    / "observability"
    / "agent-evaluation-observability"
    / "src"
)

if str(OBS_SRC) not in sys.path:
    sys.path.append(str(OBS_SRC))

from models import (  # noqa: E402
    ErrorCategory,
    EvaluationStatus,
    OperationType,
    SafeEvaluationResult,
    SafeTraceEvent,
    TraceStatus,
)
from redactor import TelemetryRedactor  # noqa: E402


def test_safe_success_output():
    """Verify that a standard successful agent turn produces valid safe telemetry."""
    dirty_payload = {
        "request_id": "req-123",
        "agent_id": "agent-v1",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 100,
        "prompt": "secret prompt",
        "correlation_id": "corr-123",
    }

    safe_data = TelemetryRedactor.filter_payload(dirty_payload)
    event = SafeTraceEvent(**safe_data)

    assert event.request_id == "req-123"
    assert event.status == TraceStatus.SUCCESS
    assert "prompt" not in safe_data
    assert not hasattr(event, "prompt")


def test_safe_failure_output():
    """Verify that a failed agent turn produces valid safe telemetry without leaking internals."""
    failure_payload = {
        "request_id": "req-failed",
        "operation_type": "tool_call",
        "status": "error",
        "duration_ms": 50,
        "error_category": "upstream_error",
        "stack_trace": "Internal error at secret_file.py:42",
        "raw_tool_payload": {"cmd": "rm -rf /"},
    }

    safe_data = TelemetryRedactor.filter_payload(failure_payload)
    event = SafeTraceEvent(**safe_data)

    assert event.status == TraceStatus.ERROR
    assert event.error_category == ErrorCategory.UPSTREAM_ERROR
    assert "stack_trace" not in safe_data
    assert "raw_tool_payload" not in safe_data


def test_forbidden_fields_redacted():
    """Ensure that explicitly forbidden fields never cross the boundary."""
    forbidden_keys = [
        "prompt",
        "api_key",
        "credentials",
        "stack_trace",
        "raw_response",
        "tenant_id",
        "subscription_id",
    ]

    dirty_payload = {key: "sensitive-value" for key in forbidden_keys}
    dirty_payload.update(
        {
            "request_id": "req-1",
            "operation_type": "agent_turn",
            "status": "success",
            "duration_ms": 10,
        }
    )

    safe_data = TelemetryRedactor.filter_payload(dirty_payload)

    for key in forbidden_keys:
        assert key not in safe_data


def test_invalid_telemetry_rejected():
    """Verify that oversized or invalid telemetry is rejected by the shared contract."""
    # Invalid duration (oversized)
    with pytest.raises(ValidationError):
        SafeTraceEvent(
            request_id="req-1",
            operation_type=OperationType.AGENT_TURN,
            status=TraceStatus.SUCCESS,
            duration_ms=4000000,  # Max is 3600000
        )

    # Invalid request_id (illegal characters)
    with pytest.raises(ValidationError):
        SafeTraceEvent(
            request_id="req-123!!!",
            operation_type=OperationType.AGENT_TURN,
            status=TraceStatus.SUCCESS,
            duration_ms=100,
        )


def test_evaluation_result_validation():
    """Verify that SafeEvaluationResult strictly follows the schema."""
    valid_result = {
        "evaluation_id": "eval-1",
        "request_id": "req-1",
        "metrics": {
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 4.0,
            "safe_failure_behavior": True,
        },
        "status": "pass",
    }

    result = SafeEvaluationResult(**valid_result)
    assert result.status == EvaluationStatus.PASS

    # Invalid cost (oversized)
    invalid_result = valid_result.copy()
    invalid_result["metrics"]["estimated_cost_usd"] = 100.0  # Max is 10.0

    with pytest.raises(ValidationError):
        SafeEvaluationResult(**invalid_result)
