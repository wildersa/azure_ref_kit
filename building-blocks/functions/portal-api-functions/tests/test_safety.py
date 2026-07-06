import pytest
import logging
import json
from unittest.mock import MagicMock
from src.adapters import StorageAdapter
from src.worker import PortalWorker

def test_safety_boundary_no_exception_leak(caplog):
    # Setup
    adapter = StorageAdapter()
    # Mocking _get_table_client to raise an exception
    adapter._get_table_client = MagicMock(side_effect=Exception("SENSITIVE_DB_ERROR_CONNECTION_STRING_ABC123"))

    # Execute
    with caplog.at_level(logging.ERROR):
        runs = adapter.get_runs("cust-1")

    # Assert
    assert runs == []
    for record in caplog.records:
        assert "SENSITIVE_DB_ERROR_CONNECTION_STRING_ABC123" not in record.message
        assert "ABC123" not in record.message
    assert "Error fetching runs for customer" in caplog.text

def test_safety_boundary_no_storage_ref_in_output():
    # Setup
    mock_adapter = MagicMock(spec=StorageAdapter)
    worker = PortalWorker(adapter=mock_adapter)

    mock_adapter.get_run.return_value = {"PartitionKey": "cust-1", "RowKey": "run-1"}
    mock_adapter.get_artifacts.return_value = [
        {
            "id": "art-1",
            "safe_name": "doc.pdf",
            "storage_ref": "https://mystorage.blob.core.windows.net/artifacts/run-1/doc.pdf?sas=token"
        }
    ]

    # Execute
    artifacts = worker.get_artifacts("cust-1", "run-1")

    # Assert
    output_str = json.dumps(artifacts)
    assert "mystorage.blob.core.windows.net" not in output_str
    assert "sas=token" not in output_str
    assert "storage_ref" not in output_str
    assert "download_url" in output_str

def test_safety_boundary_sanitized_run_details():
    # Setup
    mock_adapter = MagicMock(spec=StorageAdapter)
    worker = PortalWorker(adapter=mock_adapter)

    mock_adapter.get_run.return_value = {
        "PartitionKey": "cust-1",
        "RowKey": "run-1",
        "internal_id": "secret-123",
        "raw_logs": "technical detail",
        "status": "completed",
        "pipeline_type": "test",
        "created_at": "2023-01-01"
    }
    mock_adapter.get_steps.return_value = []

    # Execute
    run = worker.get_run_detail("cust-1", "run-1")

    # Assert
    output_str = json.dumps(run)
    assert "internal_id" not in run
    assert "secret-123" not in output_str
    assert "raw_logs" not in run
    assert "technical detail" not in output_str
