import re
from typing import Any, Dict, Set, Optional
from .models import TechnicalTelemetry, OperationStatus

# Standard redaction patterns for common sensitive formats
REDACTION_PATTERNS = [
    (re.compile(r"AccountKey=[^;]+", re.IGNORECASE), "AccountKey=[REDACTED]"),
    (
        re.compile(r"Bearer\s+[a-zA-Z0-9\-\._~+/]+=*", re.IGNORECASE),
        "Bearer [REDACTED]",
    ),
    (re.compile(r"sig=[a-zA-Z0-9%]+", re.IGNORECASE), "sig=[REDACTED]"),
    (re.compile(r"client_secret=[^&]+", re.IGNORECASE), "client_secret=[REDACTED]"),
    (re.compile(r"password=[^&;]+", re.IGNORECASE), "password=[REDACTED]"),
]

# Explicitly forbidden fields that must never be included in telemetry
FORBIDDEN_FIELDS: Set[str] = {
    "prompt",
    "prompts",
    "user_input",
    "system_message",
    "system_instruction",
    "token",
    "tokens",
    "access_token",
    "api_key",
    "secret",
    "secrets",
    "credentials",
    "connection_string",
    "sas_url",
    "stack_trace",
    "stacktrace",
    "payload",
    "raw_payload",
    "request_body",
    "response_body",
    "customer_id",
    "tenant_id",
    "subscription_id",
    "user_id",
    "pii",
    "phi",
}


class TelemetryRedactor:
    """
    Utility to ensure telemetry data adheres to the safe boundary contract.
    """

    @staticmethod
    def redact_value(value: Any) -> Any:
        """Apply pattern-based redaction if the value is a string."""
        if not isinstance(value, str):
            return value

        redacted = value
        for pattern, replacement in REDACTION_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @staticmethod
    def sanitize_to_safe_telemetry(
        operation_name: str,
        operation_status: OperationStatus,
        duration_ms: int,
        request_id: Optional[str] = None,
        component_name: Optional[str] = None,
        target_resource: Optional[str] = None,
        custom_dimensions: Optional[Dict[str, str]] = None,
    ) -> TechnicalTelemetry:
        """
        Constructs a validated and redacted TechnicalTelemetry object.
        Enforces stricter bounds on dimensions count and key/value length.
        """

        safe_custom_dims = {}
        if custom_dimensions:
            # 1. Limit entry count to 20
            count = 0
            for key, val in custom_dimensions.items():
                if count >= 20:
                    break

                key_lower = key.lower()

                # 2. Skip forbidden fields
                if key_lower in FORBIDDEN_FIELDS:
                    continue

                # 3. Truncate keys to 64 chars and values to 512 chars
                truncated_key = key[:64]
                redacted_val = TelemetryRedactor.redact_value(str(val))
                truncated_val = redacted_val[:512]

                safe_custom_dims[truncated_key] = truncated_val
                count += 1

        return TechnicalTelemetry(
            operation_name=TelemetryRedactor.redact_value(operation_name),
            operation_status=operation_status,
            duration_ms=duration_ms,
            request_id=TelemetryRedactor.redact_value(request_id)
            if request_id
            else None,
            component_name=TelemetryRedactor.redact_value(component_name)
            if component_name
            else None,
            target_resource=TelemetryRedactor.redact_value(target_resource)
            if target_resource
            else None,
            custom_dimensions=safe_custom_dims if safe_custom_dims else None,
        )
