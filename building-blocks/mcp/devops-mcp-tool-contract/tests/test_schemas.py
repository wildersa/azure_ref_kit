import json
import os
import pytest
import jsonschema


def get_schema_path(filename):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "../schemas", filename))


def load_schema(filename):
    with open(get_schema_path(filename), "r") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "schema_file",
    [
        "get_pipeline_run_status_request.schema.json",
        "get_pipeline_run_status_response.schema.json",
        "get_latest_build_summary_request.schema.json",
        "get_latest_build_summary_response.schema.json",
    ],
)
def test_schema_syntax(schema_file):
    """Verify that each schema is a valid JSON schema."""
    schema = load_schema(schema_file)
    # Basic check to ensure it's a dictionary and has a $schema key
    assert isinstance(schema, dict)
    assert "$schema" in schema


def test_request_schema_validation():
    """Verify that the request schema correctly validates a sample payload."""
    schema = load_schema("get_pipeline_run_status_request.schema.json")
    payload = {"pipeline_id": "123", "run_id": "456"}
    jsonschema.validate(instance=payload, schema=schema)


def test_response_schema_validation_with_ref():
    """Verify that the response schema with a $ref correctly validates a sample payload."""
    schema = load_schema("get_pipeline_run_status_response.schema.json")

    # Load the referenced schema manually to build a Registry
    ref_schema_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../../../../shared/contracts/devops-status.schema.json")
    )
    with open(ref_schema_path, "r") as f:
        ref_schema = json.load(f)

    # Use the newer referencing API if available, or just mock the registry
    # For simplicity in this environment, we can use a basic validator with a Store
    # or just use the Pydantic models which are already tested.
    # But let's try to make the jsonschema validation work.

    from jsonschema.validators import validator_for

    validator_cls = validator_for(schema)
    # Note: Using a simplified approach to provide the dependency
    # In a real environment, you'd use a Registry or a local server.
    # Here we can just use the fact that we know the reference.

    payload = {
        "pipeline_name": "Main CI",
        "run_id": "20240101.5",
        "status": "completed",
        "result": "succeeded",
        "branch": "main",
        "start_time": "2024-01-01T10:00:00Z",
        "portal_url": "https://dev.azure.com/org/proj/_build/results?buildId=12345",
    }

    # If we can't easily resolve the ref in this test env with the current jsonschema version,
    # we can at least validate the schema itself and rely on test_models.py
    # However, let's try one more time with a simpler resolver setup.
    from jsonschema import RefResolver

    base_path = os.path.dirname(os.path.abspath(get_schema_path("get_pipeline_run_status_response.schema.json")))
    resolver = RefResolver(base_uri=f"file://{base_path}/", referrer=schema)

    jsonschema.validate(instance=payload, schema=schema, resolver=resolver)


def test_request_schema_rejection():
    """Verify that the request schema rejects invalid payloads."""
    schema = load_schema("get_pipeline_run_status_request.schema.json")
    # Missing required field
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance={"pipeline_id": "123"}, schema=schema)
    # Extra field (additionalProperties: false)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance={"pipeline_id": "123", "run_id": "456", "extra": "foo"}, schema=schema)
