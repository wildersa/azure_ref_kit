import json
import azure.functions as func
from function_app import get_system_status

def test_get_system_status_returns_200_and_json():
    # Construct a mock HTTP request
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/system_status'
    )

    # Call the function
    resp = get_system_status(req)

    # Validate the response
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'

    body = json.loads(resp.get_body())
    assert body['business_status'] == 'operational'
    assert 'service_health' in body
    assert 'active_regions' in body
    assert 'last_updated' in body

def test_get_system_status_safe_boundary():
    # Verify it doesn't leak sensitive fields (negative test for the boundary)
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/system_status'
    )

    resp = get_system_status(req)
    body = json.loads(resp.get_body())

    forbidden_fields = ['secret', 'token', 'connection_string', 'raw_logs', 'stack_trace']
    for field in forbidden_fields:
        assert field not in body, f"Leaked forbidden field: {field}"
