import pytest
from src.redactor import TelemetryRedactor

def test_redactor_removes_forbidden_fields():
    """Verify that forbidden fields are stripped from the payload."""
    dirty_payload = {
        "request_id": "req-123",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 150,
        "prompt": "What is the secret key?",
        "tokens": 42,
        "credentials": {"key": "secret-value"},
        "stack_trace": "Error at line 10...",
    }

    safe_payload = TelemetryRedactor.filter_payload(dirty_payload)

    assert "request_id" in safe_payload
    assert "operation_type" in safe_payload
    assert "prompt" not in safe_payload
    assert "tokens" not in safe_payload
    assert "credentials" not in safe_payload
    assert "stack_trace" not in safe_payload

def test_redactor_applies_pattern_redaction():
    """Verify that sensitive patterns in strings are redacted."""
    payload = {
        "request_id": "req-123",
        "operation_type": "tool_call",
        "status": "failure",
        "duration_ms": 100,
        "error_category": "Auth failed: Bearer secret-token-123 and AccountKey=abc-123",
    }

    safe_payload = TelemetryRedactor.filter_payload(payload)

    error_msg = safe_payload["error_category"]
    assert "Bearer [REDACTED]" in error_msg
    assert "AccountKey=[REDACTED]" in error_msg
    assert "secret-token-123" not in error_msg
    assert "abc-123" not in error_msg

def test_redactor_only_allows_allowlisted_fields():
    """Verify that unknown fields are removed even if not explicitly forbidden."""
    payload = {
        "request_id": "req-123",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 50,
        "internal_debugging_flag": True,
        "another_hidden_field": "hidden",
    }

    safe_payload = TelemetryRedactor.filter_payload(payload)

    assert "request_id" in safe_payload
    assert "internal_debugging_flag" not in safe_payload
    assert "another_hidden_field" not in safe_payload

def test_is_safe_check():
    """Verify the is_safe check correctly identifies dirty payloads."""
    assert TelemetryRedactor.is_safe({"request_id": "123"}) is True
    assert TelemetryRedactor.is_safe({"prompt": "hello"}) is False
    assert TelemetryRedactor.is_safe({"tokens": 10}) is False
    assert TelemetryRedactor.is_safe({"tenant_id": "uuid"}) is False
