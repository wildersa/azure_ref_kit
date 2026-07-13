from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_agent_query_valid():
    payload = {"query_type": "status_summary", "resource_id": "vm-123"}
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "summary" in data
    assert "vm-123" in data["summary"]


def test_agent_query_invalid_payload():
    # Missing resource_id
    payload = {"query_type": "status_summary"}
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 422


def test_agent_query_invalid_chars():
    # Invalid characters in resource_id
    payload = {"query_type": "status_summary", "resource_id": "vm-123!"}
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 422


def test_agent_query_too_long():
    # resource_id too long (> 64)
    payload = {"query_type": "status_summary", "resource_id": "a" * 65}
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 422


def test_error_boundary_redacts_technical_details(caplog):
    from unittest.mock import patch

    # Mock the response_model validation or the handler to raise an unexpected error
    with patch("src.main.AgentQueryResponse") as mock_model:
        mock_model.side_effect = Exception("Sensitive database error: user=admin")

        payload = {"query_type": "status_summary", "resource_id": "vm-123"}
        response = client.post("/agent/query", json=payload)

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "INTERNAL_ERROR"
        assert (
            data["friendly_message"]
            == "An unexpected error occurred while processing the agent request."
        )

        # Verify the sensitive info is NOT in the logs (only our generic message)
        assert "An unexpected error occurred in the agent API" in caplog.text
        assert "Sensitive database error" not in caplog.text


def test_extra_fields_forbidden():
    payload = {
        "query_type": "status_summary",
        "resource_id": "vm-123",
        "extra_field": "not-allowed",
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 422
