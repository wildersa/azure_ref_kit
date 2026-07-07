import json
import jsonschema
import pytest
from pathlib import Path


def test_system_status_contract():
    # Path to the schema
    schema_path = (
        Path(__file__).parent.parent / "contracts" / "system-status.schema.json"
    )
    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Valid sample response
    valid_response = {
        "business_status": "operational",
        "service_health": "Healthy",
        "active_regions": ["eastus", "westus2"],
        "last_updated": "2026-07-03T10:00:00Z",
        "environment": "production",
    }

    # Validate valid response
    jsonschema.validate(instance=valid_response, schema=schema)

    # Invalid response (missing required field)
    invalid_response_missing = {
        "business_status": "operational",
        "service_health": "Healthy",
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_response_missing, schema=schema)

    # Invalid response (wrong type)
    invalid_response_wrong_type = {
        "business_status": "operational",
        "service_health": "Healthy",
        "active_regions": "eastus",  # Should be array
        "last_updated": "2026-07-03T10:00:00Z",
        "environment": "production",
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=invalid_response_wrong_type, schema=schema)
