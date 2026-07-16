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
        "completion": "The final answer.",
        "generated_text": "More text.",
        "azure_resource_id": "/subscriptions/abc/resourceGroups/xyz/...",
    }

    safe_payload = TelemetryRedactor.filter_payload(dirty_payload)

    assert "customer_id" not in safe_payload
    assert "user_id" not in safe_payload
    assert "raw_logs" not in safe_payload
    assert "completion" not in safe_payload
    assert "generated_text" not in safe_payload
    assert "azure_resource_id" not in safe_payload


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


def test_redactor_redacts_azure_resource_ids():
    """Verify that Azure Resource IDs are redacted within strings."""
    payload = {
        "request_id": "req-123",
        "operation_type": "agent_turn",
        "status": "error",
        "duration_ms": 50,
        "error_category": "Resource /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-rg/providers/Microsoft.CognitiveServices/accounts/my-ai not found.",
    }

    safe_payload = TelemetryRedactor.filter_payload(payload)
    error_msg = safe_payload["error_category"]
    assert "/subscriptions/[REDACTED]/resourceGroups/[REDACTED]" in error_msg
    assert "my-rg" not in error_msg


def test_redactor_enforces_payload_size_limit():
    """Verify that the redactor limits the number of fields in the output."""
    large_payload = {f"field_{i}": "value" for i in range(50)}
    # Add some allowlisted fields so they have a chance to be included
    large_payload["request_id"] = "req-1"
    large_payload["status"] = "success"

    safe_payload = TelemetryRedactor.filter_payload(large_payload)

    assert len(safe_payload) <= 20


def test_redactor_truncates_allowlisted_strings():
    """Verify that the redactor truncates string values for allowlisted fields."""
    payload = {
        "request_id": "req-1",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 10,
        "sanitized_summary": "a" * 1000,
    }

    safe_payload = TelemetryRedactor.filter_payload(payload)
    assert len(safe_payload["sanitized_summary"]) == 512


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


def test_redactor_allows_newly_added_fields():
    """Verify that newly added fields are allowed through the redactor."""
    payload = {
        "request_id": "req-1",
        "operation_type": "tool_call",
        "status": "success",
        "duration_ms": 10,
        "tool_outcome": "success",
        "safety_outcome": "Pass",
        "sanitized_summary": "Summary text.",
    }

    safe_payload = TelemetryRedactor.filter_payload(payload)

    assert safe_payload["tool_outcome"] == "success"
    assert safe_payload["safety_outcome"] == "Pass"
    assert safe_payload["sanitized_summary"] == "Summary text."
