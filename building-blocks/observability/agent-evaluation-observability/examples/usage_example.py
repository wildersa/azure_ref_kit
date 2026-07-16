import json
import sys
from pathlib import Path

# Add src to path
SRC_DIR = Path(__file__).parent.parent / "src"
sys.path.append(str(SRC_DIR))

from redactor import TelemetryRedactor  # noqa: E402
from models import SafeTraceEvent, LatencyBucket  # noqa: E402


def get_latency_bucket(duration_ms: int) -> LatencyBucket:
    if duration_ms < 1000:
        return LatencyBucket.UNDER_1S
    elif duration_ms < 5000:
        return LatencyBucket.S1_TO_5S
    elif duration_ms < 15000:
        return LatencyBucket.S5_TO_15S
    else:
        return LatencyBucket.OVER_15S


def main():
    print("--- Safe Telemetry Usage Example ---")

    # 1. Simulate a raw agent turn payload with sensitive and non-allowlisted data
    raw_payload = {
        "request_id": "req-123",
        "agent_id": "assistant-v1",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 1250,
        "prompt": "What is the secret key?",  # Forbidden
        "completion": "The secret key is 42.",  # Forbidden
        "azure_resource_id": "/subscriptions/abc-123/resourceGroups/my-rg/providers/Microsoft.CognitiveServices/accounts/my-ai",  # Forbidden
        "api_key": "sk-12345",  # Forbidden
        "internal_id": "hidden-999",  # Not allowlisted
    }

    print("\n[Raw Payload Keys]:", list(raw_payload.keys()))

    # 2. Redact and filter the payload
    safe_data = TelemetryRedactor.filter_payload(raw_payload)

    # 3. Add derived safe fields
    safe_data["latency_bucket"] = get_latency_bucket(raw_payload["duration_ms"])
    safe_data["evaluation_score"] = 4.5  # Simulated quality signal

    print("\n[Safe Payload Data]:")
    print(json.dumps(safe_data, indent=2))

    # 4. Validate with Pydantic model
    try:
        safe_event = SafeTraceEvent(**safe_data)
        print("\n[Validated SafeTraceEvent]:")
        print(safe_event.model_dump_json(indent=2))
    except Exception as e:
        print(f"\n[Validation Error]: {e}")


if __name__ == "__main__":
    main()
