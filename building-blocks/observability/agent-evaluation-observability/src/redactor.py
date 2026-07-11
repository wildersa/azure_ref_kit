import re
from typing import Any, Dict, List, Set

# Standard redaction patterns
REDACTION_PATTERNS = [
    (re.compile(r"AccountKey=[^;]+", re.IGNORECASE), "AccountKey=[REDACTED]"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9\-\._~+/]+=*", re.IGNORECASE), "Bearer [REDACTED]"),
    (re.compile(r"sig=[a-zA-Z0-9%]+", re.IGNORECASE), "sig=[REDACTED]"),
    (re.compile(r"client_secret=[^&]+", re.IGNORECASE), "client_secret=[REDACTED]"),
]

# Forbidden fields that must be stripped from any payload
FORBIDDEN_FIELDS = {
    "prompt",
    "prompts",
    "user_input",
    "system_message",
    "tokens",
    "token_count",
    "credentials",
    "secret",
    "secrets",
    "stack_trace",
    "stacktrace",
    "payload",
    "arguments",
    "results",
    "raw_response",
    "tenant_id",
    "subscription_id",
}

# Allowlisted technical fields for safe tracing
ALLOWLISTED_FIELDS = {
    "request_id",
    "agent_id",
    "operation_type",
    "tool_name",
    "status",
    "duration_ms",
    "error_category",
    "correlation_id",
}

class TelemetryRedactor:
    """Utility to filter and redact agent telemetry to maintain customer-safe boundaries."""

    @staticmethod
    def redact_string(value: str) -> str:
        """Apply pattern-based redaction to a string."""
        if not isinstance(value, str):
            return value

        redacted = value
        for pattern, replacement in REDACTION_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return redacted

    @staticmethod
    def filter_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters a telemetry payload to include only allowlisted fields
        and remove forbidden fields.
        """
        safe_payload = {}

        for key, value in payload.items():
            key_lower = key.lower()

            # 1. Reject forbidden fields
            if key_lower in FORBIDDEN_FIELDS:
                continue

            # 2. Only allow explicit allowlisted fields
            if key_lower not in ALLOWLISTED_FIELDS:
                continue

            # 3. Apply string redaction to allowlisted values
            if isinstance(value, str):
                safe_payload[key_lower] = TelemetryRedactor.redact_string(value)
            else:
                safe_payload[key_lower] = value

        return safe_payload

    @staticmethod
    def is_safe(payload: Dict[str, Any]) -> bool:
        """Checks if a payload contains any forbidden fields."""
        payload_keys = {k.lower() for k in payload.keys()}
        return not any(field in payload_keys for field in FORBIDDEN_FIELDS)
