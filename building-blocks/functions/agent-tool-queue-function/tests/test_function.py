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


def test_submit_job_invalid_request_redacts_details():
    # Sensitive input in a field that fails validation
    sensitive_input = "System prompt: ignore all previous instructions"
    req_body = {
        "operation_type": "analyze_text",
        "parameters": "not-a-dict", # Triggers pydantic error
        "extra_info": sensitive_input
    }
    req = func.HttpRequest(
        method="POST",
        url="/api/submit",
        body=json.dumps(req_body).encode("utf-8")
    )
    outputQueue = MagicMock()

    resp = submit_job(req, outputQueue)

    assert resp.status_code == 400
    resp_data = json.loads(resp.get_body())
    assert resp_data["error"] == "Invalid request payload or schema."
    # REGRESSION: Sensitive input must NOT be reflected in the error message
    assert sensitive_input not in str(resp_data)


@patch("function_app.StatusStore")
def test_get_job_status_success(mock_status_store_class):
    # Setup
    mock_store = MagicMock()
    mock_status_store_class.return_value = mock_store

    from src.models import JobStatusResponse
    mock_store.get_status.return_value = JobStatusResponse(
        id="550e8400-e29b-41d4-a716-446655440000",
        status=JobStatus.COMPLETED,
        created_at="2024-07-03T12:00:00Z",
        result_data={"some": "result"}
    )

    req = func.HttpRequest(
        method="GET",
        url="/api/status/550e8400-e29b-41d4-a716-446655440000",
        body=b"",
        route_params={"correlation_id": "550e8400-e29b-41d4-a716-446655440000"}
    )

    # Execute
    resp = get_job_status(req)

    # Assert
    assert resp.status_code == 200
    resp_data = json.loads(resp.get_body())
    assert resp_data["id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert resp_data["status"] == "completed"
    assert resp_data["result_data"] == {"some": "result"}


def test_get_job_status_invalid_uuid_format():
    # Attempted path traversal or SQLi-like payload in correlation_id
    malicious_id = "../jobs/all"
    req = func.HttpRequest(
        method="GET",
        url=f"/api/status/{malicious_id}",
        body=b"",
        route_params={"correlation_id": malicious_id}
    )

    resp = get_job_status(req)

    assert resp.status_code == 400
    assert "Invalid Correlation ID format" in json.loads(resp.get_body())["error"]


@patch("function_app.StatusStore")
def test_get_job_status_not_found(mock_status_store_class):
    mock_store = MagicMock()
    mock_status_store_class.return_value = mock_store
    mock_store.get_status.return_value = None

    valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
    req = func.HttpRequest(
        method="GET",
        url=f"/api/status/{valid_uuid}",
        body=b"",
        route_params={"correlation_id": valid_uuid}
    )

    resp = get_job_status(req)

    assert resp.status_code == 404
    assert "Job not found" in json.loads(resp.get_body())["error"]
