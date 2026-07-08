from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


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
