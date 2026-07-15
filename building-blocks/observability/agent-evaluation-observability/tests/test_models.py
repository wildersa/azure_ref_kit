import pytest
from pydantic import ValidationError
from src.models import (
    SafeTraceEvent,
    SafeEvaluationResult,
    OperationType,
    EvaluationStatus,
    ToolName,
)


def test_safe_trace_event_valid():
    """Verify a valid trace event passes validation."""
    event_data = {
        "request_id": "req-123",
        "agent_id": "agent-v1",
        "operation_type": "tool_call",
        "tool_name": "get_pipeline_status",
        "status": "success",
        "duration_ms": 150,
        "correlation_id": "df-run-999",
    }
    event = SafeTraceEvent(**event_data)
    assert event.request_id == "req-123"
    assert event.operation_type == OperationType.TOOL_CALL
    assert event.tool_name == ToolName.GET_PIPELINE_STATUS


def test_safe_trace_event_allows_unauthorized_tool_placeholder():
    """Verify that the redacted placeholder for unauthorized tools is accepted."""
    event_data = {
        "request_id": "req-123",
        "operation_type": "tool_call",
        "tool_name": "[UNAUTHORIZED_TOOL]",
        "status": "failure",
        "duration_ms": 10,
    }
    event = SafeTraceEvent(**event_data)
    assert event.tool_name == ToolName.UNAUTHORIZED_TOOL


def test_safe_trace_event_rejects_extra_fields():
    """Verify SafeTraceEvent rejects fields not in the schema."""
    event_data = {
        "request_id": "req-123",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 150,
        "prompt": "this should be rejected",
    }
    with pytest.raises(ValidationError):
        SafeTraceEvent(**event_data)


def test_safe_trace_event_strict_id_pattern():
    """Verify SafeTraceEvent IDs follow the SAFE_ID_PATTERN."""
    # Invalid characters in ID
    with pytest.raises(ValidationError):
        SafeTraceEvent(
            request_id="req#123",
            operation_type="agent_turn",
            status="success",
            duration_ms=100,
        )


def test_safe_evaluation_result_valid():
    """Verify a valid evaluation result passes validation."""
    result_data = {
        "evaluation_id": "eval-001",
        "request_id": "req-123",
        "metrics": {
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 4.5,
            "safe_failure_behavior": True,
            "latency_ms": 1200,
            "estimated_cost_usd": 0.05,
        },
        "status": "pass",
    }
    result = SafeEvaluationResult(**result_data)
    assert result.status == EvaluationStatus.PASS
    assert result.metrics.groundedness_score == 4.5


def test_safe_evaluation_result_rejects_extra_metrics():
    """Verify EvaluationMetrics rejects extra fields."""
    result_data = {
        "evaluation_id": "eval-001",
        "request_id": "req-123",
        "metrics": {
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 4.5,
            "safe_failure_behavior": True,
            "raw_payload": "should fail",
        },
        "status": "pass",
    }
    with pytest.raises(ValidationError):
        SafeEvaluationResult(**result_data)


def test_safe_evaluation_result_out_of_range_score():
    """Verify groundedness_score is bounded [0, 5]."""
    result_data = {
        "evaluation_id": "eval-001",
        "request_id": "req-123",
        "metrics": {
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 5.1,
            "safe_failure_behavior": True,
        },
        "status": "pass",
    }
    with pytest.raises(ValidationError):
        SafeEvaluationResult(**result_data)


def test_trace_event_prohibited_data_types():
    """Verify duration_ms must be non-negative."""
    with pytest.raises(ValidationError):
        SafeTraceEvent(
            request_id="req-123",
            operation_type="agent_turn",
            status="success",
            duration_ms=-1,
        )


def test_safe_trace_event_rejects_oversized_duration():
    """Verify that oversized duration_ms is rejected."""
    with pytest.raises(ValidationError) as excinfo:
        SafeTraceEvent(
            request_id="req-123",
            operation_type="agent_turn",
            status="success",
            duration_ms=3600001,  # 1 hour + 1 ms
        )
    assert "duration_ms" in str(excinfo.value)


def test_safe_evaluation_result_rejects_oversized_metrics():
    """Verify that oversized metrics are rejected."""
    # Oversized latency
    result_data_latency = {
        "evaluation_id": "eval-001",
        "request_id": "req-123",
        "metrics": {
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 4.5,
            "safe_failure_behavior": True,
            "latency_ms": 3600001,
        },
        "status": "pass",
    }
    with pytest.raises(ValidationError) as excinfo:
        SafeEvaluationResult(**result_data_latency)
    assert "latency_ms" in str(excinfo.value)

    # Oversized cost
    result_data_cost = {
        "evaluation_id": "eval-001",
        "request_id": "req-123",
        "metrics": {
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 4.5,
            "safe_failure_behavior": True,
            "estimated_cost_usd": 10.01,
        },
        "status": "pass",
    }
    with pytest.raises(ValidationError) as excinfo:
        SafeEvaluationResult(**result_data_cost)
    assert "estimated_cost_usd" in str(excinfo.value)
