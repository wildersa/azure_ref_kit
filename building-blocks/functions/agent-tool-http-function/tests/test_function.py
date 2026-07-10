import json
import sys
import os
import azure.functions as func
import pytest
import pydantic
from datetime import datetime

# Add the parent directory to sys.path so we can import function_app and src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from function_app import get_system_status
from src.models import SystemStatusResponse, ErrorResponse


@pytest.fixture
def success_fixture():
    with open(
        os.path.join(os.path.dirname(__file__), "../fixtures/success_status.json"), "r"
    ) as f:
        return json.load(f)


def test_get_system_status_returns_200_and_valid_model():
    # Construct a mock HTTP request
    req = func.HttpRequest(method="GET", body=None, url="/api/system_status")

    # Call the function
    resp = get_system_status(req)

    # Validate the response
    assert resp.status_code == 200
    assert resp.mimetype == "application/json"

    body = json.loads(resp.get_body())

    # Validate against Pydantic model
    model = SystemStatusResponse(**body)
    assert model.business_status == "operational"
    assert model.service_health == "healthy"
    assert "eastus" in model.active_regions
    assert isinstance(model.last_updated, datetime)


def test_system_status_matches_success_fixture(success_fixture):
    # This ensures our runtime behavior matches our documented success fixture
    # Note: last_updated will differ, so we check other fields
    req = func.HttpRequest(method="GET", body=None, url="/api/system_status")
    resp = get_system_status(req)
    body = json.loads(resp.get_body())

    assert body["business_status"] == success_fixture["business_status"]
    assert body["service_health"] == success_fixture["service_health"]
    assert body["active_regions"] == success_fixture["active_regions"]
    assert body["environment"] == success_fixture["environment"]


def test_get_system_status_safe_boundary():
    # Verify it doesn't leak sensitive fields
    req = func.HttpRequest(method="GET", body=None, url="/api/system_status")

    resp = get_system_status(req)
    body = json.loads(resp.get_body())

    forbidden_fields = [
        "secret",
        "token",
        "connection_string",
        "raw_logs",
        "stack_trace",
        "subscription_id",
        "internal_url",
    ]
    for field in forbidden_fields:
        assert field not in body, f"Leaked forbidden field: {field}"


def test_system_status_model_extra_fields_forbidden():
    # Test that the model itself forbids extra fields
    with pytest.raises(pydantic.ValidationError):
        SystemStatusResponse(
            business_status="operational",
            service_health="healthy",
            active_regions=["eastus"],
            last_updated=datetime.now(),
            environment="prod",
            extra_field="should_not_be_here",
        )


def test_error_response_model():
    error_data = {
        "error_code": "TEST_ERROR",
        "friendly_message": "A safe error message.",
    }
    model = ErrorResponse(**error_data)
    assert model.error_code == "TEST_ERROR"
    assert model.friendly_message == "A safe error message."
