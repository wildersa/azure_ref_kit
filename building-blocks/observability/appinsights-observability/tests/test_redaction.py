from src.redactor import TelemetryRedactor
from src.models import OperationStatus


def test_redact_value_bearer():
    """Verify that Bearer tokens are redacted."""
    redacted = TelemetryRedactor.redact_value("Bearer 12345-abcde")
    assert redacted == "Bearer [REDACTED]"


def test_redact_value_account_key():
    """Verify that Azure AccountKeys are redacted."""
    redacted = TelemetryRedactor.redact_value("AccountKey=secret-key-123;")
    assert redacted == "AccountKey=[REDACTED];"


def test_redact_value_sig():
    """Verify that SAS signatures (sig=) are redacted."""
    redacted = TelemetryRedactor.redact_value("https://example.com?sig=topsecret")
    assert redacted == "https://example.com?sig=[REDACTED]"


def test_sanitize_to_safe_telemetry_strips_forbidden_fields():
    """Verify that forbidden fields are removed from custom_dimensions."""
    safe_telemetry = TelemetryRedactor.sanitize_to_safe_telemetry(
        operation_name="test",
        operation_status=OperationStatus.SUCCESS,
        duration_ms=100,
        custom_dimensions={
            "prompt": "Tell me a secret",
            "safe_key": "safe_value",
            "api_key": "12345",
        },
    )

    assert "safe_key" in safe_telemetry.custom_dimensions
    assert "prompt" not in safe_telemetry.custom_dimensions
    assert "api_key" not in safe_telemetry.custom_dimensions
    assert safe_telemetry.custom_dimensions["safe_key"] == "safe_value"


def test_sanitize_to_safe_telemetry_redacts_values():
    """Verify that values in safe telemetry are also redacted if they match patterns."""
    safe_telemetry = TelemetryRedactor.sanitize_to_safe_telemetry(
        operation_name="test",
        operation_status=OperationStatus.SUCCESS,
        duration_ms=100,
        request_id="Bearer 12345",
        custom_dimensions={"debug_info": "AccountKey=xyz"},
    )

    assert safe_telemetry.request_id == "Bearer [REDACTED]"
    assert safe_telemetry.custom_dimensions["debug_info"] == "AccountKey=[REDACTED]"


def test_sanitize_enforces_dimension_count_limit():
    """Verify that dimensions beyond the limit of 20 are dropped."""
    many_dims = {f"key_{i}": f"val_{i}" for i in range(30)}
    safe_telemetry = TelemetryRedactor.sanitize_to_safe_telemetry(
        operation_name="test",
        operation_status=OperationStatus.SUCCESS,
        duration_ms=100,
        custom_dimensions=many_dims,
    )
    assert len(safe_telemetry.custom_dimensions) == 20


def test_sanitize_enforces_key_length_limit():
    """Verify that keys longer than 64 chars are truncated."""
    long_key = "a" * 100
    safe_telemetry = TelemetryRedactor.sanitize_to_safe_telemetry(
        operation_name="test",
        operation_status=OperationStatus.SUCCESS,
        duration_ms=100,
        custom_dimensions={long_key: "val"},
    )
    truncated_key = long_key[:64]
    assert truncated_key in safe_telemetry.custom_dimensions
    assert safe_telemetry.custom_dimensions[truncated_key] == "val"


def test_sanitize_enforces_value_length_limit():
    """Verify that values longer than 512 chars are truncated."""
    long_val = "v" * 600
    safe_telemetry = TelemetryRedactor.sanitize_to_safe_telemetry(
        operation_name="test",
        operation_status=OperationStatus.SUCCESS,
        duration_ms=100,
        custom_dimensions={"key": long_val},
    )
    assert safe_telemetry.custom_dimensions["key"] == long_val[:512]
