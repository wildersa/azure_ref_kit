import pytest
from pydantic import ValidationError
from src.models import TechnicalTelemetry, OperationStatus


def test_valid_telemetry():
    """Verify that a valid telemetry object is correctly instantiated."""
    telemetry = TechnicalTelemetry(
        operation_name="process_document",
        operation_status=OperationStatus.SUCCESS,
        duration_ms=150,
        request_id="req-123",
        component_name="ocr-worker",
        target_resource="blob-storage",
        custom_dimensions={"model_version": "v1.2"},
    )
    assert telemetry.operation_name == "process_document"
    assert telemetry.operation_status == OperationStatus.SUCCESS
    assert telemetry.duration_ms == 150
    assert telemetry.request_id == "req-123"


def test_invalid_operation_status():
    """Verify that invalid operation status raises a ValidationError."""
    with pytest.raises(ValidationError):
        TechnicalTelemetry(
            operation_name="test", operation_status="NOT_AN_ENUM", duration_ms=100
        )


def test_extra_fields_forbidden():
    """Verify that extra fields are not allowed (extra='forbid')."""
    with pytest.raises(ValidationError):
        TechnicalTelemetry(
            operation_name="test",
            operation_status=OperationStatus.SUCCESS,
            duration_ms=100,
            unknown_field="unauthorized",
        )


def test_oversized_duration():
    """Verify that duration_ms must be <= 3,600,000 (1 hour)."""
    with pytest.raises(ValidationError):
        TechnicalTelemetry(
            operation_name="test",
            operation_status=OperationStatus.SUCCESS,
            duration_ms=3600001,
        )


def test_negative_duration():
    """Verify that duration_ms must be >= 0."""
    with pytest.raises(ValidationError):
        TechnicalTelemetry(
            operation_name="test",
            operation_status=OperationStatus.SUCCESS,
            duration_ms=-1,
        )


def test_invalid_identifier_pattern():
    """Verify that identifiers must match the SAFE_ID_PATTERN."""
    with pytest.raises(ValidationError):
        TechnicalTelemetry(
            operation_name="invalid@name",
            operation_status=OperationStatus.SUCCESS,
            duration_ms=100,
        )
