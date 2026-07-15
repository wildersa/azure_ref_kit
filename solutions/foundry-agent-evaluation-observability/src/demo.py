import sys
import json
from pathlib import Path

# Add building blocks to sys.path
REPO_ROOT = Path(__file__).parent.parent.parent.parent
OBS_SRC = (
    REPO_ROOT
    / "building-blocks"
    / "observability"
    / "agent-evaluation-observability"
    / "src"
)

if str(OBS_SRC) not in sys.path:
    sys.path.append(str(OBS_SRC))

from models import SafeEvaluationResult, EvaluationStatus, SafeTraceEvent  # noqa: E402
from redactor import TelemetryRedactor  # noqa: E402


def run_demo():
    print("--- Foundry Agent Evaluation and Observability Demo ---")
    print("\n1. Simulating a Raw Agent Turn (Dirty Payload)")

    dirty_payload = {
        "request_id": "req-12345",
        "agent_id": "devops-assistant-v1",
        "operation_type": "tool_call",
        "tool_name": "get_pipeline_status",
        "status": "success",
        "duration_ms": 1250,
        "prompt": "What is the status of pipeline 123?",
        "api_key": "sk-hidden-secret",
        "raw_response": {
            "status": "Succeeded",
            "id": 123,
            "logs": "All tests passed...",
        },
        "correlation_id": "df-run-789",
    }

    print(
        f"Raw payload contains forbidden fields: {[k for k in dirty_payload.keys() if k in ['prompt', 'api_key', 'raw_response']]}"
    )

    print("\n2. Applying Telemetry Redactor")
    safe_data = TelemetryRedactor.filter_payload(dirty_payload)

    try:
        safe_event = SafeTraceEvent(**safe_data)
        print("Success: Produced SafeTraceEvent")
        print(json.dumps(safe_event.model_dump(), indent=2))
    except Exception as e:
        print(f"Error: Failed to produce SafeTraceEvent: {e}")

    print("\n3. Generating Safe Evaluation Result")
    eval_result = SafeEvaluationResult(
        evaluation_id="eval-001",
        request_id="req-12345",
        metrics={
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 4.8,
            "safe_failure_behavior": True,
            "latency_ms": 1250,
            "estimated_cost_usd": 0.005,
        },
        status=EvaluationStatus.PASS,
    )
    print(json.dumps(eval_result.model_dump(), indent=2))

    print("\n4. Simulating a Safe Failure Path (Redacting Stack Trace)")
    failure_payload = {
        "request_id": "req-failed-1",
        "operation_type": "agent_turn",
        "status": "error",
        "duration_ms": 500,
        "error_category": "upstream_error",
        "stack_trace": "Traceback (most recent call last):\n  File 'app.py', line 10...\nConnectionError: Failed to connect to DevOps API",
        "internal_debug_info": "User session expired at 2026-07-03T10:00:00Z",
    }

    safe_failure_data = TelemetryRedactor.filter_payload(failure_payload)
    safe_failure_event = SafeTraceEvent(**safe_failure_data)

    print(
        f"Safe failure event produced with error_category: {safe_failure_event.error_category}"
    )
    print(
        f"Forbidden field 'stack_trace' present: {'stack_trace' in safe_failure_data}"
    )
    print(
        f"Unknown field 'internal_debug_info' present: {'internal_debug_info' in safe_failure_data}"
    )

    print("\n--- Demo Complete ---")


if __name__ == "__main__":
    run_demo()
