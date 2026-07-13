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
