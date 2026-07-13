import pytest
from unittest.mock import MagicMock
import json
from src.tool import process_queue_job, StatusStore
from src.models import JobStatus


@pytest.fixture
def mock_store():
    store = MagicMock(spec=StatusStore)
    return store


def test_process_queue_job_ping_success(mock_store):
    payload = {
        "correlation_id": "test-job-12345678",
        "operation_type": "ping",
        "parameters": {"text": "hello"},
    }
    result = process_queue_job(payload, store=mock_store)

    assert result.correlation_id == "test-job-12345678"
    assert result.status == JobStatus.COMPLETED
    assert result.result_data == {"message": "pong", "echo": "hello"}

    # Verify status transitions were recorded
    assert mock_store.update_status.call_count == 2
    # First call: RUNNING
    args, kwargs = mock_store.update_status.call_args_list[0]
    assert args[1] == JobStatus.RUNNING
    # Second call: COMPLETED
    args, kwargs = mock_store.update_status.call_args_list[1]
    assert args[1] == JobStatus.COMPLETED


def test_process_queue_job_analyze_text_success(mock_store):
    payload = {
        "correlation_id": "analyze-12345678",
        "operation_type": "analyze_text",
        "parameters": {"text": "Hello World"},
    }
    result = process_queue_job(payload, store=mock_store)

    assert result.correlation_id == "analyze-12345678"
    assert result.status == JobStatus.COMPLETED
    assert result.result_data["word_count"] == 2
    assert result.result_data["length"] == 11


def test_process_queue_job_invalid_operation(mock_store):
    payload = {
        "correlation_id": "invalid-op-12345678",
        "operation_type": "unknown_op",
        "parameters": {},
    }
    result = process_queue_job(payload, store=mock_store)

    assert result.correlation_id == "invalid-op-12345678"
    assert result.status == JobStatus.FAILED
    assert "Unsupported operation type" in result.error_message

    # Verify FAILED status was persisted
    args, kwargs = mock_store.update_status.call_args_list[-1]
    assert args[1] == JobStatus.FAILED


def test_process_queue_job_invalid_schema(mock_store):
    # Missing operation_type
    payload = {
        "correlation_id": "schema-fail-12345678",
        "parameters": {},
    }
    result = process_queue_job(payload, store=mock_store)

    assert result.correlation_id == "schema-fail-12345678"
    assert result.status == JobStatus.FAILED
    assert "Invalid job payload or schema" in result.error_message


def test_process_queue_job_invalid_correlation_id_format(mock_store):
    # Too short
    payload = {
        "correlation_id": "short",
        "operation_type": "ping",
        "parameters": {},
    }
    result = process_queue_job(payload, store=mock_store)

    assert result.status == JobStatus.FAILED
    assert result.correlation_id == "invalid-id-format"


def test_process_queue_job_extra_fields_forbidden(mock_store):
    payload = {
        "correlation_id": "extra-field-12345678",
        "operation_type": "ping",
        "parameters": {},
        "unsafe_field": "exploit"
    }
    result = process_queue_job(payload, store=mock_store)

    assert result.status == JobStatus.FAILED
    assert "Invalid job payload or schema" in result.error_message


def test_process_queue_job_redacts_unexpected_error(mock_store):
    # Pass None to trigger an Exception in the validation step
    result = process_queue_job(None, store=mock_store)

    assert result.status == JobStatus.FAILED
    assert "Invalid job payload or schema" in result.error_message
    # Ensure invalid-id-format is used when payload is missing
    assert result.correlation_id == "invalid-id-format"
