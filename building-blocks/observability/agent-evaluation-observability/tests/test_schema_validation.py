import json
import os
from jsonschema import validate

def test_trace_event_fixture_validates_against_schema():
    """Verify that the safe trace event fixture complies with its schema."""
    base_path = os.path.join(os.path.dirname(__file__), "..")
    schema_path = os.path.join(base_path, "trace-event.schema.json")
    fixture_path = os.path.join(base_path, "tests/fixtures/safe-trace-event.json")

    with open(schema_path, "r") as f:
        schema = json.load(f)
    with open(fixture_path, "r") as f:
        fixture = json.load(f)

    validate(instance=fixture, schema=schema)

def test_trace_event_rejects_forbidden_fields():
    """Verify that the trace event schema rejects forbidden additional properties."""
    base_path = os.path.join(os.path.dirname(__file__), "..")
    schema_path = os.path.join(base_path, "trace-event.schema.json")
    with open(schema_path, "r") as f:
        schema = json.load(f)

    import pytest
    from jsonschema import ValidationError

    # Test with forbidden field 'prompt'
    invalid_trace = {
        "request_id": "req-001",
        "operation_type": "agent_turn",
        "status": "success",
        "duration_ms": 100,
        "prompt": "forbidden"
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_trace, schema=schema)

    # Test with unauthorized 'error_category'
    invalid_trace_error = {
        "request_id": "req-001",
        "operation_type": "agent_turn",
        "status": "error",
        "duration_ms": 100,
        "error_category": "Internal Server Error: stack trace at..."
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_trace_error, schema=schema)

def test_evaluation_result_rejects_forbidden_metrics():
    """Verify that the evaluation result schema rejects additional properties in metrics."""
    base_path = os.path.join(os.path.dirname(__file__), "..")
    schema_path = os.path.join(base_path, "evaluation-result.schema.json")
    with open(schema_path, "r") as f:
        schema = json.load(f)

    from jsonschema import ValidationError
    import pytest

    # Test with forbidden metric 'raw_payload'
    invalid_eval = {
        "evaluation_id": "eval-1",
        "request_id": "req-1",
        "status": "pass",
        "metrics": {
            "task_completion": True,
            "safe_tool_use": True,
            "groundedness_score": 5,
            "safe_failure_behavior": True,
            "raw_payload": "{}"
        }
    }
    with pytest.raises(ValidationError):
        validate(instance=invalid_eval, schema=schema)

def test_evaluation_result_fixture_validates_against_schema():
    """Verify that the safe evaluation result fixture complies with its schema."""
    base_path = os.path.join(os.path.dirname(__file__), "..")
    schema_path = os.path.join(base_path, "evaluation-result.schema.json")
    fixture_path = os.path.join(base_path, "tests/fixtures/safe-evaluation-result.json")

    with open(schema_path, "r") as f:
        schema = json.load(f)
    with open(fixture_path, "r") as f:
        fixture = json.load(f)

    validate(instance=fixture, schema=schema)
