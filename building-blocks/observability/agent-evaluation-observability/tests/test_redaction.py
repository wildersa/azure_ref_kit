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


def test_redactor_removes_new_forbidden_fields():
    """Verify that newly added forbidden fields are stripped from the payload."""
    dirty_payload = {
        "request_id": "req-123",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 150,
        "customer_id": "cust-999",
        "user_id": "user-888",
        "raw_logs": "DEBUG: internal details",
    }

    safe_payload = TelemetryRedactor.filter_payload(dirty_payload)

    assert "customer_id" not in safe_payload
    assert "user_id" not in safe_payload
    assert "raw_logs" not in safe_payload


def test_redactor_removes_more_forbidden_fields():
    """Verify that even more forbidden fields are stripped from the payload."""
    dirty_payload = {
        "request_id": "req-123",
        "api_key": "sk-12345",
        "connection_string": "Endpoint=sb://...;SharedAccessKey=...",
        "raw_tool_payload": {"sensitive": "data"},
        "system_instruction": "You are a secret agent.",
    }

    safe_payload = TelemetryRedactor.filter_payload(dirty_payload)

    assert "api_key" not in safe_payload
    assert "connection_string" not in safe_payload
    assert "raw_tool_payload" not in safe_payload
    assert "system_instruction" not in safe_payload


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


def test_tool_name_allowlist_validation():
    """Verify that only allowlisted tool names are preserved."""
    # Allowed tool
    payload_allowed = {
        "request_id": "1",
        "operation_type": "tool_call",
        "status": "success",
        "duration_ms": 1,
        "tool_name": "get_pipeline_status",
    }
    safe_allowed = TelemetryRedactor.filter_payload(payload_allowed)
    assert safe_allowed["tool_name"] == "get_pipeline_status"

    # Unauthorized tool
    payload_unauthorized = {
        "request_id": "1",
        "operation_type": "tool_call",
        "status": "success",
        "duration_ms": 1,
        "tool_name": "delete_all_resources",
    }
    safe_unauthorized = TelemetryRedactor.filter_payload(payload_unauthorized)
    assert safe_unauthorized["tool_name"] == "[UNAUTHORIZED_TOOL]"


def test_strict_allowlist_check():
    """Verify the strict allowlist check identifies unknown fields."""
    # Valid
    assert (
        TelemetryRedactor.has_only_allowlisted_fields(
            {
                "request_id": "123",
                "status": "success",
                "duration_ms": 10,
                "operation_type": "agent_turn",
            }
        )
        is True
    )

    # Forbidden field
    assert (
        TelemetryRedactor.has_only_allowlisted_fields(
            {"request_id": "123", "prompt": "hello"}
        )
        is False
    )

    # Unknown field (not allowlisted)
    assert (
        TelemetryRedactor.has_only_allowlisted_fields(
            {"request_id": "123", "unknown_technical_field": "val"}
        )
        is False
    )
