from fastapi.testclient import TestClient
from src.main import app

# Initialize TestClient with raise_server_exceptions=False to test exception handlers
client = TestClient(app, raise_server_exceptions=False)


def test_health_endpoint():
    """
    Verify the health endpoint returns a successful status and timestamp.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_agent_query_valid_input():
    """
    Verify the agent query endpoint with valid input.
    """
    payload = {"query_type": "status_summary", "resource_id": "res-123"}
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "summary" in data
    assert "updated_at" in data


def test_agent_query_invalid_query_type():
    """
    Verify the agent query endpoint rejects invalid query_type (regex mismatch).
    """
    payload = {"query_type": "invalid status!", "resource_id": "res-123"}
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 422  # Validation error


def test_agent_query_invalid_resource_id():
    """
    Verify the agent query endpoint rejects invalid resource_id (too long).
    """
    payload = {"query_type": "status", "resource_id": "a" * 65}
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 422  # Validation error


def test_agent_query_extra_fields():
    """
    Verify the agent query endpoint rejects extra fields (ConfigDict(extra="forbid")).
    """
    payload = {
        "query_type": "status",
        "resource_id": "res-123",
        "malicious_field": "leak",
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 422


def test_global_exception_handler_redaction():
    """
    Verify that technical details are redacted on internal errors.
    """
    payload = {"query_type": "status", "resource_id": "trigger-error"}
    response = client.post("/agent/query", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert data["error_code"] == "INTERNAL_ERROR"
    assert "unexpected error" in data["friendly_message"].lower()
    # Ensure the sensitive message is NOT in the response
    assert "Triggered" not in data["friendly_message"]
