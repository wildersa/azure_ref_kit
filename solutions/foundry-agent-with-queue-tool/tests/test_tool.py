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


@patch("requests.post")
def test_submit_task_fails_on_extra_fields(mock_post, settings):
    """Verify that extra fields from the provider cause validation failure (fail-closed)."""
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "correlation_id": "test-uuid",
        "status": "pending",
        "internal_secret": "do-not-leak",
    }
    mock_post.return_value = mock_response

    result = submit_task("ping", settings=settings)

    assert "error" in result
    assert "invalid response" in result["error"]


@patch("requests.post")
def test_submit_task_fails_on_oversized_id(mock_post, settings):
    """Verify that oversized correlation_id is rejected."""
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {
        "correlation_id": "a" * 100,
        "status": "pending",
    }
    mock_post.return_value = mock_response

    result = submit_task("ping", settings=settings)

    assert "error" in result
    assert "invalid response" in result["error"]


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


@patch("requests.get")
def test_get_task_status_fails_on_oversized_payload(mock_get, settings):
    """Verify that oversized fields in status response are rejected."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    # Test oversized summary
    mock_response.json.return_value = {
        "id": "test-uuid-12345",
        "status": "completed",
        "business_summary": "s" * 1000,
    }
    mock_get.return_value = mock_response
    result = get_task_status("test-uuid-12345", settings=settings)
    assert "error" in result

    # Test too many keys in result_data
    mock_response.json.return_value = {
        "id": "test-uuid-12345",
        "status": "completed",
        "result_data": {f"key{i}": i for i in range(20)},
    }
    result = get_task_status("test-uuid-12345", settings=settings)
    assert "error" in result

    # Test oversized value in result_data
    mock_response.json.return_value = {
        "id": "test-uuid-12345",
        "status": "completed",
        "result_data": {"large": "v" * 2000},
    }
    result = get_task_status("test-uuid-12345", settings=settings)
    assert "error" in result


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
