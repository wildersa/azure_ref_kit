from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_status_endpoint():
    task_id = "test-123"
    response = client.get(f"/status/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "summary" in data
    assert task_id in data["summary"]
    # Ensure no technical details are leaked
    assert "internal" not in data["summary"].lower()
    assert "log" not in data["summary"].lower()
    assert "stack" not in data["summary"].lower()
    assert "trace" not in data["summary"].lower()
