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
