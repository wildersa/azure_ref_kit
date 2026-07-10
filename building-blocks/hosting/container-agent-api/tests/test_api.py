from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_agent_request_valid():
    payload = {"request_type": "summarize", "payload": "Helpful content"}
    response = client.post("/agent/request", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "summary" in data


def test_agent_request_invalid():
    payload = {"request_type": "summarize"}  # Missing payload
    response = client.post("/agent/request", json=payload)
    assert response.status_code == 422


def test_status_endpoint_valid():
    task_id = "test-123"
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "summary" in data
    # Ensure the raw task_id is NOT reflected in the summary
    assert task_id not in data["summary"]
    # Ensure no technical details are leaked
    assert "internal" not in data["summary"].lower()
    assert "log" not in data["summary"].lower()


def test_status_endpoint_invalid_chars():
    # Characters that are typically escaped or restricted
    task_id = "test_123!"
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 422  # Unprocessable Entity due to validation failure


def test_status_endpoint_too_long():
    task_id = "a" * 65
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 422


def test_error_boundary_logs_safe_and_returns_500(caplog):
    # Force an error by patching a dependency or using a route that fails
    # Since it's a small app, we can mock get_status to raise an exception
    from unittest.mock import patch

    with patch("src.main.handle_get_status") as mock_handle:
        mock_handle.side_effect = Exception("Sensitive database error: user=admin")

        response = client.get("/status/test-123")

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "INTERNAL_ERROR"
        assert (
            data["friendly_message"]
            == "An unexpected error occurred while processing the agent request."
        )

        # Verify the sensitive info is NOT in the logs if we were checking specific strings,
        # but our handler specifically logs a generic message.
        assert "An unexpected error occurred in the agent API" in caplog.text
        assert "Sensitive database error" not in caplog.text
