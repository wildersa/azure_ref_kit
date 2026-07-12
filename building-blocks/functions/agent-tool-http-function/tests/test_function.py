import json
import azure.functions as func
from function_app import get_resource_info_trigger

def test_get_resource_info_trigger_success():
    """Test the HTTP trigger with a valid request."""
    req_body = {
        "resource_id": "vm-prod-a",
        "resource_type": "virtual_machine"
    }
    req = func.HttpRequest(
        method="POST",
        body=json.dumps(req_body).encode("utf-8"),
        url="/api/get_resource_info"
    )

    resp = get_resource_info_trigger(req)

    assert resp.status_code == 200
    resp_data = json.loads(resp.get_body())
    assert resp_data["resource_id"] == "vm-prod-a"
    assert resp_data["status"] == "running"

def test_get_resource_info_trigger_invalid_json():
    """Test the HTTP trigger with invalid JSON."""
    req = func.HttpRequest(
        method="POST",
        body=b"not a json",
        url="/api/get_resource_info"
    )

    resp = get_resource_info_trigger(req)

    assert resp.status_code == 400
    resp_data = json.loads(resp.get_body())
    assert "error" in resp_data
    assert resp_data["error"] == "Invalid JSON body."

def test_get_resource_info_trigger_validation_error():
    """Test the HTTP trigger with missing fields."""
    req_body = {"resource_id": "only-id"}
    req = func.HttpRequest(
        method="POST",
        body=json.dumps(req_body).encode("utf-8"),
        url="/api/get_resource_info"
    )

    resp = get_resource_info_trigger(req)

    assert resp.status_code == 400
    resp_data = json.loads(resp.get_body())
    assert "error" in resp_data
