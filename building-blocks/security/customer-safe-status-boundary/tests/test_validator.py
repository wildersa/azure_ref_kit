import pytest
import jsonschema
from src.validator import (
    validate_status,
    sanitize_status,
    validate_failure,
    sanitize_failure,
)


def test_validate_status_valid():
    valid_status = {
        "id": "run-123",
        "status": "completed",
        "business_summary": "Process completed successfully.",
        "progress_percent": 100,
        "estimated_cost": 0.05,
        "created_at": "2026-07-03T12:00:00Z",
        "safe_artifacts": [
            {
                "name": "result.pdf",
                "size_bytes": 1024,
                "content_type": "application/pdf",
            }
        ],
    }
    validate_status(valid_status)


def test_validate_status_invalid_additional_property():
    invalid_status = {
        "id": "run-123",
        "status": "completed",
        "created_at": "2026-07-03T12:00:00Z",
        "internal_log": "DEBUG: internal info",
    }
    with pytest.raises(jsonschema.ValidationError) as excinfo:
        validate_status(invalid_status)
    assert "internal_log" in str(excinfo.value)


def test_validate_status_invalid_pattern():
    invalid_status = {
        "id": "/subscriptions/abc/resourceGroups/xyz",  # Invalid characters / and :
        "status": "completed",
        "created_at": "2026-07-03T12:00:00Z",
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_status(invalid_status)


def test_validate_status_oversized_artifacts():
    invalid_status = {
        "id": "run-123",
        "status": "completed",
        "created_at": "2026-07-03T12:00:00Z",
        "safe_artifacts": [{"name": f"f{i}.txt", "size_bytes": 10} for i in range(51)],
    }
    with pytest.raises(jsonschema.ValidationError) as excinfo:
        validate_status(invalid_status)
    assert "is too long" in str(excinfo.value)


def test_sanitize_status_deterministic():
    input_data = {
        "id": "run-123",
        "status": "completed",
        "created_at": "2026-07-03T12:00:00Z",
        "internal_log": "DEBUG: internal info",
    }
    first_pass = sanitize_status(input_data)
    second_pass = sanitize_status(input_data)
    assert first_pass == second_pass
    assert first_pass is not second_pass  # Should be a new object


def test_sanitize_status_removes_forbidden_fields():
    input_data = {
        "id": "run-123",
        "status": "completed",
        "created_at": "2026-07-03T12:00:00Z",
        "internal_log": "DEBUG: internal info",
        "stack_trace": "at main.py line 10",
        "safe_artifacts": [
            {"name": "result.pdf", "size_bytes": 1024, "internal_id": "secret-blob-id"}
        ],
    }
    sanitized = sanitize_status(input_data)

    assert "id" in sanitized
    assert "status" in sanitized
    assert "created_at" in sanitized
    assert "internal_log" not in sanitized
    assert "stack_trace" not in sanitized
    assert "safe_artifacts" in sanitized
    assert "internal_id" not in sanitized["safe_artifacts"][0]
    assert sanitized["safe_artifacts"][0]["name"] == "result.pdf"


def test_input_immutability():
    input_data = {
        "id": "run-123",
        "status": "completed",
        "created_at": "2026-07-03T12:00:00Z",
        "internal_log": "DEBUG: internal info",
    }
    sanitize_status(input_data)
    assert "internal_log" in input_data  # Original object should not be mutated


def test_validate_failure_valid():
    valid_failure = {
        "error_code": "INVALID_INPUT",
        "message": "The provided document is unreadable.",
        "correlation_id": "corr-987654321",
    }
    validate_failure(valid_failure)


def test_validate_failure_invalid_code():
    invalid_failure = {
        "error_code": "invalid code with spaces",
        "message": "Error message",
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_failure(invalid_failure)


def test_sanitize_failure():
    input_data = {
        "error_code": "AUTH_ERROR",
        "message": "Access denied.",
        "raw_exception": "403 Forbidden: Missing token",
    }
    sanitized = sanitize_failure(input_data)
    assert "error_code" in sanitized
    assert "message" in sanitized
    assert "raw_exception" not in sanitized


def test_oversized_strings():
    invalid_status = {
        "id": "run-123",
        "status": "completed",
        "created_at": "2026-07-03T12:00:00Z",
        "business_summary": "A" * 1001,  # Max is 1000
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_status(invalid_status)
