import pytest
import sys
import os
from unittest.mock import MagicMock
import azure.durable_functions as df
from datetime import datetime, timezone

# Add parent directory to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestrator import pipeline_orchestrator


@pytest.fixture
def mock_context():
    context = MagicMock(spec=df.DurableOrchestrationContext)
    context.instance_id = "test-run-id"
    context.current_utc_datetime = datetime(2023, 1, 1, tzinfo=timezone.utc)
    return context


def test_orchestrator_oversized_id(mock_context):
    oversized_id = "a" * 65
    invalid_input = {
        "pipeline_run": {
            "id": oversized_id,
            "customer_id": "cust-123",
            "pipeline_type": "invoice-processing",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
        }
    }
    mock_context.get_input.return_value = invalid_input

    gen = pipeline_orchestrator(mock_context)
    with pytest.raises(StopIteration) as exc:
        next(gen)
    assert exc.value.value["status"] == "failed"
    assert "Contract validation failed" in exc.value.value["error"]


def test_orchestrator_oversized_source_blob(mock_context):
    oversized_blob = "b" * 2049
    invalid_input = {
        "pipeline_run": {
            "id": "test-id",
            "customer_id": "cust-123",
            "pipeline_type": "invoice-processing",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
        },
        "source_blob": oversized_blob,
    }
    mock_context.get_input.return_value = invalid_input

    gen = pipeline_orchestrator(mock_context)
    with pytest.raises(StopIteration) as exc:
        next(gen)
    assert exc.value.value["status"] == "failed"
    assert "Contract validation failed" in exc.value.value["error"]


def test_orchestrator_oversized_status_update(mock_context):
    valid_input = {
        "pipeline_run": {
            "id": "test-id",
            "customer_id": "cust-123",
            "pipeline_type": "invoice-processing",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
        }
    }
    mock_context.get_input.return_value = valid_input

    # Mock OCR returning too many artifacts (exceeding maxItems: 100)
    oversized_artifacts = ["artifact-" + str(i) for i in range(101)]
    ocr_too_many_artifacts = {
        "status": "completed",
        "artifacts": oversized_artifacts,
    }

    gen = pipeline_orchestrator(mock_context)

    # 1. Start overall
    next(gen)

    # 2. Start OCR step
    gen.send(None)

    # 3. OCR call
    gen.send(None)

    # 4. Send oversized artifacts.
    # In my orchestrator, _update_step is called with artifacts.
    # This calls jsonschema.validate(instance=step_data, schema=PIPELINE_STEP_SCHEMA)
    # Since it's inside a try/except Exception, it should NOT raise StopIteration here,
    # but instead it will proceed to the except block, yield the failed status updates,
    # and THEN raise StopIteration with the failure result.

    # Yield step failure status
    gen.send(ocr_too_many_artifacts)

    # Yield run failure status
    gen.send(None)

    # Raise StopIteration
    with pytest.raises(StopIteration) as exc:
        gen.send(None)

    assert exc.value.value["status"] == "failed"
    # Friendly failure message from the catch-all except block
    assert "An error occurred" in exc.value.value["friendly_message"]


def test_orchestrator_oversized_artifact_id(mock_context):
    valid_input = {
        "pipeline_run": {
            "id": "test-id",
            "customer_id": "cust-123",
            "pipeline_type": "invoice-processing",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
        }
    }
    mock_context.get_input.return_value = valid_input

    # Mock OCR returning an artifact ID that is too long (maxLength: 128)
    long_artifact_id = "a" * 129
    ocr_long_artifact = {
        "status": "completed",
        "artifacts": [long_artifact_id],
    }

    gen = pipeline_orchestrator(mock_context)

    # 1. Start overall
    next(gen)

    # 2. Start OCR step
    gen.send(None)

    # 3. OCR call
    gen.send(None)

    # 4. Send long artifact ID.
    # Yield step failure status
    gen.send(ocr_long_artifact)

    # Yield run failure status
    gen.send(None)

    # Raise StopIteration
    with pytest.raises(StopIteration) as exc:
        gen.send(None)

    assert exc.value.value["status"] == "failed"
    assert "An error occurred" in exc.value.value["friendly_message"]
