import pytest
from unittest.mock import MagicMock, patch
import json
import azure.functions as func
from function_app import submit_job, get_job_status
from src.models import JobStatus


@patch("function_app.StatusStore")
@patch("function_app.uuid.uuid4")
def test_submit_job_success(mock_uuid, mock_status_store_class):
    # Setup
    mock_uuid.return_value = "550e8400-e29b-41d4-a716-446655440000"
    mock_store = MagicMock()
    mock_status_store_class.return_value = mock_store

    req_body = {
        "operation_type": "analyze_text",
        "parameters": {"text": "hello test"}
    }
    req = func.HttpRequest(
        method="POST",
        url="/api/submit",
        body=json.dumps(req_body).encode("utf-8")
    )
    outputQueue = MagicMock()

    # Execute
    resp = submit_job(req, outputQueue)

    # Assert
    assert resp.status_code == 202
    resp_data = json.loads(resp.get_body())
    assert resp_data["correlation_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert resp_data["status"] == "pending"

    # Verify persistence
    mock_store.update_status.assert_called_once()
    args, kwargs = mock_store.update_status.call_args
    assert args[0] == "550e8400-e29b-41d4-a716-446655440000"
    assert args[1] == JobStatus.PENDING

    # Verify queue message
    outputQueue.set.assert_called_once()
    queue_msg = json.loads(outputQueue.set.call_args[0][0])
    assert queue_msg["correlation_id"] == "550e8400-e29b-41d4-a716-446655440000"


def test_submit_job_invalid_request():
    req = func.HttpRequest(
        method="POST",
        url="/api/submit",
        body=json.dumps({"wrong_field": "data"}).encode("utf-8")
    )
    outputQueue = MagicMock()

    resp = submit_job(req, outputQueue)

    assert resp.status_code == 400
    assert "Invalid request" in json.loads(resp.get_body())["error"]


@patch("function_app.StatusStore")
def test_get_job_status_success(mock_status_store_class):
    # Setup
    mock_store = MagicMock()
    mock_status_store_class.return_value = mock_store

    from src.models import JobStatusResponse
    mock_store.get_status.return_value = JobStatusResponse(
        id="test-id-12345678",
        status=JobStatus.COMPLETED,
        created_at="2024-07-03T12:00:00Z",
        result_data={"some": "result"}
    )

    req = func.HttpRequest(
        method="GET",
        url="/api/status/test-id-12345678",
        body=b"",
        route_params={"correlation_id": "test-id-12345678"}
    )

    # Execute
    resp = get_job_status(req)

    # Assert
    assert resp.status_code == 200
    resp_data = json.loads(resp.get_body())
    assert resp_data["id"] == "test-id-12345678"
    assert resp_data["status"] == "completed"
    assert resp_data["result_data"] == {"some": "result"}


@patch("function_app.StatusStore")
def test_get_job_status_not_found(mock_status_store_class):
    mock_store = MagicMock()
    mock_status_store_class.return_value = mock_store
    mock_store.get_status.return_value = None

    req = func.HttpRequest(
        method="GET",
        url="/api/status/unknown",
        body=b"",
        route_params={"correlation_id": "unknown"}
    )

    resp = get_job_status(req)

    assert resp.status_code == 404
    assert "Job not found" in json.loads(resp.get_body())["error"]
