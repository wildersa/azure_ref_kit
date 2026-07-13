import json
import os
import pytest
import jsonschema


def get_schema_path(filename):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../schemas", filename)
    )


def load_schema(filename):
    with open(get_schema_path(filename), "r") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "schema_file",
    [
        "get_pipeline_run_status_request.schema.json",
        "get_pipeline_run_status_response.schema.json",
        "list_recent_pipeline_runs_request.schema.json",
        "list_recent_pipeline_runs_response.schema.json",
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


def test_list_runs_request_schema_validation():
    """Verify that the list runs request schema validates correctly."""
    schema = load_schema("list_recent_pipeline_runs_request.schema.json")
    payload = {"pipeline_id": "123", "branch": "main", "top": 10}
    jsonschema.validate(instance=payload, schema=schema)


def test_response_schema_validation_with_ref():
    """Verify that the response schema with a $ref correctly validates a sample payload."""
    schema = load_schema("get_pipeline_run_status_response.schema.json")

    # Load the shared schema to populate the resolver's store
    shared_schema_path = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "../../../../shared/contracts/devops-status.schema.json",
        )
    )
    with open(shared_schema_path, "r") as f:
        shared_schema = json.load(f)

    # The expected URI after resolution
    shared_uri = "https://github.com/wildersa/azure_ref_kit/shared/contracts/devops-status.schema.json"

    # To handle relative $ref during testing, we need a resolver with a store
    from jsonschema import RefResolver

    store = {shared_uri: shared_schema}
    resolver = RefResolver(base_uri=schema["$id"], referrer=schema, store=store)

    payload = {
        "pipeline_name": "Main CI",
        "run_id": "20240101.5",
        "status": "completed",
        "result": "succeeded",
        "branch": "main",
        "start_time": "2024-01-01T10:00:00Z",
        "portal_url": "https://dev.azure.com/org/proj/_build/results?buildId=12345",
    }
    jsonschema.validate(instance=payload, schema=schema, resolver=resolver)


def test_request_schema_rejection():
    """Verify that the request schema rejects invalid payloads."""
    schema = load_schema("get_pipeline_run_status_request.schema.json")
    # Missing required field
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance={"pipeline_id": "123"}, schema=schema)
    # Extra field (additionalProperties: false)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance={"pipeline_id": "123", "run_id": "456", "extra": "foo"},
            schema=schema,
        )


def test_request_schema_security_rejection():
    """Verify that the request schema rejects unsafe identifiers."""
    schema = load_schema("get_pipeline_run_status_request.schema.json")

    # Path traversal attempt
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance={"pipeline_id": "../../etc/passwd", "run_id": "123"}, schema=schema
        )

    # URL/Protocol injection attempt
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance={"pipeline_id": "http://malicious.com", "run_id": "123"},
            schema=schema,
        )

    # Empty string (minLength: 1)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance={"pipeline_id": "", "run_id": "123"}, schema=schema
        )

    # Overly long string (maxLength: 128)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(
            instance={"pipeline_id": "a" * 129, "run_id": "123"}, schema=schema
        )


def get_fixture_path(filename):
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../fixtures", filename)
    )


def load_fixture(filename):
    with open(get_fixture_path(filename), "r") as f:
        return json.load(f)


@pytest.mark.parametrize(
    "fixture_file, schema_file",
    [
        ("pipeline_run_status.json", "get_pipeline_run_status_response.schema.json"),
        ("recent_pipeline_runs.json", "list_recent_pipeline_runs_response.schema.json"),
    ],
)
def test_fixtures_against_schemas(fixture_file, schema_file):
    """Verify that all fixtures are valid against their respective schemas."""
    fixture = load_fixture(fixture_file)
    schema = load_schema(schema_file)

    if "$ref" in schema:
        # Handle relative $ref for responses that use shared contracts
        shared_schema_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../../shared/contracts/devops-status.schema.json",
            )
        )
        with open(shared_schema_path, "r") as f:
            shared_schema = json.load(f)
        shared_uri = "https://github.com/wildersa/azure_ref_kit/shared/contracts/devops-status.schema.json"
        from jsonschema import RefResolver

        store = {shared_uri: shared_schema}
        resolver = RefResolver(base_uri=schema["$id"], referrer=schema, store=store)
        jsonschema.validate(instance=fixture, schema=schema, resolver=resolver)
    else:
        jsonschema.validate(instance=fixture, schema=schema)
