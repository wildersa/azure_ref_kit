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
    "customer_id",
    "user_id",
    "raw_logs",
    "token",
    "api_key",
    "access_token",
    "raw_request",
    "raw_payload",
    "raw_tool_payload",
    "raw_provider_payload",
    "connection_string",
    "system_instruction",
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

# Controlled allowlist for tool names to prevent arbitrary string leakage
ALLOWED_TOOL_NAMES = {
    "get_pipeline_status",
    "list_artifacts",
    "get_build_log_summary",
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
        and strictly validates controlled values like tool_name.
        """
        safe_payload = {}

        for key, value in payload.items():
            key_lower = key.lower()

            # 1. Reject forbidden fields (redundant with allowlist but kept for clarity)
            if key_lower in FORBIDDEN_FIELDS:
                continue

            # 2. Only allow explicit allowlisted fields
            if key_lower not in ALLOWLISTED_FIELDS:
                continue

            # 3. Strictly validate tool_name against a controlled allowlist
            if key_lower == "tool_name":
                if value not in ALLOWED_TOOL_NAMES:
                    safe_payload[key_lower] = "[UNAUTHORIZED_TOOL]"
                    continue

            # 4. Apply string redaction to allowlisted values
            if isinstance(value, str):
                safe_payload[key_lower] = TelemetryRedactor.redact_string(value)
            else:
                safe_payload[key_lower] = value

        return safe_payload

    @staticmethod
    def has_only_allowlisted_fields(payload: Dict[str, Any]) -> bool:
        """
        Strictly checks if a payload contains only allowlisted fields
        and no unknown or forbidden fields.
        """
        payload_keys = {k.lower() for k in payload.keys()}

        # Must not contain any forbidden fields
        if any(field in payload_keys for field in FORBIDDEN_FIELDS):
            return False

        # Must only contain fields from the allowlist
        if not payload_keys.issubset(ALLOWLISTED_FIELDS):
            return False

        return True
