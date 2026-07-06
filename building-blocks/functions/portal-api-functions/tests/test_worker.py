import pytest
from unittest.mock import MagicMock
from src.worker import PortalWorker
from src.adapters import StorageAdapter


@pytest.fixture
def mock_adapter():
    return MagicMock(spec=StorageAdapter)


@pytest.fixture
def worker(mock_adapter):
    return PortalWorker(adapter=mock_adapter)


def test_get_recent_runs_scoping(worker, mock_adapter):
    # Setup
    customer_id = "cust-1"
    mock_adapter.get_runs.return_value = [
        {
            "PartitionKey": "cust-1",
            "RowKey": "run-1",
            "pipeline_type": "tax-form",
            "status": "completed",
            "created_at": "2023-01-01T00:00:00Z",
        },
        {
            "PartitionKey": "cust-1",
            "RowKey": "run-2",
            "pipeline_type": "invoice",
            "status": "running",
            "created_at": "2023-01-02T00:00:00Z",
        },
    ]

    # Execute
    runs = worker.get_recent_runs(customer_id)

    # Assert
    assert len(runs) == 2
    assert runs[0]["id"] == "run-2"  # Sorted by created_at desc
    assert runs[1]["id"] == "run-1"
    mock_adapter.get_runs.assert_called_once_with(customer_id)


def test_get_run_detail_safety_boundary(worker, mock_adapter):
    # Setup
    customer_id = "cust-1"
    run_id = "run-1"
    mock_adapter.get_run.return_value = {
        "PartitionKey": "cust-1",
        "RowKey": "run-1",
        "pipeline_type": "tax-form",
        "status": "completed",
        "created_at": "2023-01-01T00:00:00Z",
        "internal_log": "leak-this-log",
        "connection_string": "secret-conn-string",
    }
    mock_adapter.get_steps.return_value = [
        {
            "PartitionKey": "run-1",
            "RowKey": "step-1",
            "status": "completed",
            "raw_payload": "sensitive-data",
        }
    ]

    # Execute
    run = worker.get_run_detail(customer_id, run_id)

    # Assert
    assert run["id"] == "run-1"
    assert "internal_log" not in run
    assert "connection_string" not in run
    assert len(run["steps"]) == 1
    assert "raw_payload" not in run["steps"][0]


def test_get_run_detail_not_found(worker, mock_adapter):
    # Setup
    mock_adapter.get_run.return_value = None

    # Execute
    run = worker.get_run_detail("cust-1", "run-999")

    # Assert
    assert run is None


def test_get_artifacts_scoping(worker, mock_adapter):
    # Setup
    customer_id = "cust-1"
    run_id = "run-1"
    # Mock get_run to verify ownership
    mock_adapter.get_run.return_value = {"PartitionKey": "cust-1", "RowKey": "run-1"}
    mock_adapter.get_artifacts.return_value = [{"id": "art-1", "safe_name": "doc.pdf"}]

    # Execute
    artifacts = worker.get_artifacts(customer_id, run_id)

    # Assert
    assert len(artifacts) == 1
    assert artifacts[0]["id"] == "art-1"
    mock_adapter.get_run.assert_called_with(customer_id, run_id)


def test_get_cost_summary(worker, mock_adapter):
    # Setup
    customer_id = "cust-1"
    run_id = "run-1"
    mock_adapter.get_run.return_value = {"PartitionKey": "cust-1", "RowKey": "run-1"}
    mock_adapter.get_costs.return_value = [
        {"category": "ai_tokens", "estimated_amount": 0.05},
        {"category": "storage", "estimated_amount": 0.01},
    ]

    # Execute
    summary = worker.get_cost_summary(customer_id, run_id)

    # Assert
    assert pytest.approx(summary["total_estimated_amount"]) == 0.06
    assert len(summary["breakdown"]) == 2
