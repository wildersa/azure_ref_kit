import pytest
from unittest.mock import MagicMock, patch
from src.tool_implementation import submit_task, get_task_status
from src.config import Settings


@pytest.fixture
def settings():
    return Settings(
        function_submit_url="http://mock-submit",
        function_status_url_template="http://mock-status/{correlation_id}",
    )


@patch("requests.post")
def test_submit_task_success(mock_post, settings):
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "correlation_id": "test-uuid",
        "status": "pending",
    }
    mock_post.return_value = mock_response

    result = submit_task("ping", {"text": "hello"}, settings=settings)

    assert result["correlation_id"] == "test-uuid"
    assert result["status"] == "pending"
    assert "error" not in result
    mock_post.assert_called_once_with(
        "http://mock-submit",
        json={"operation_type": "ping", "parameters": {"text": "hello"}},
        timeout=10,
    )


@patch("requests.post")
def test_submit_task_fails_on_extra_fields(mock_post, settings):
    """Verify that extra fields from the provider cause validation failure (fail-closed)."""
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "correlation_id": "test-uuid",
        "status": "pending",
        "internal_secret": "do-not-leak",
        "raw_logs": "debug info",
    }
    mock_post.return_value = mock_response

    result = submit_task("ping", settings=settings)

    assert "error" in result
    assert "invalid response" in result["error"]
    assert "internal_secret" not in str(result)
    assert "raw_logs" not in str(result)


@patch("requests.post")
def test_submit_task_failure(mock_post, settings):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    result = submit_task("ping", settings=settings)

    assert "error" in result
    assert "unavailable" in result["error"]


@patch("requests.get")
def test_get_task_status_success(mock_get, settings):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-uuid-12345",
        "status": "completed",
        "result_data": {"message": "pong"},
    }
    mock_get.return_value = mock_response

    result = get_task_status("test-uuid-12345", settings=settings)

    assert result["status"] == "completed"
    assert result["result_data"]["message"] == "pong"
    mock_get.assert_called_once_with("http://mock-status/test-uuid-12345", timeout=10)


@patch("requests.get")
def test_get_task_status_fails_on_extra_fields(mock_get, settings):
    """Verify that extra fields in status response cause validation failure (fail-closed)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-uuid-12345",
        "status": "completed",
        "internal_id": "hidden",
        "provider_payload": {"key": "val"},
    }
    mock_get.return_value = mock_response

    result = get_task_status("test-uuid-12345", settings=settings)

    assert "error" in result
    assert "invalid response" in result["error"]
    assert "internal_id" not in str(result)
    assert "provider_payload" not in str(result)


@patch("requests.get")
def test_get_task_status_not_found(mock_get, settings):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_task_status("test-uuid-nonexistent", settings=settings)

    assert "error" in result
    assert "Task not found" in result["error"]


def test_get_task_status_invalid_id(settings):
    result = get_task_status("short", settings=settings)
    assert "error" in result
    assert "Invalid correlation ID" in result["error"]
