import pytest
from unittest.mock import MagicMock
import azure.durable_functions as df
from datetime import datetime, timezone

# Import the orchestrator and activities
from src.orchestrator import pipeline_orchestrator
from src.activities import (
    update_pipeline_run_status,
    ocr_document_intelligence,
    field_validation_worker,
    final_result_publisher,
)


@pytest.fixture
def mock_context():
    context = MagicMock(spec=df.DurableOrchestrationContext)
    context.instance_id = "test-run-id"
    context.current_utc_datetime = datetime(2023, 1, 1, tzinfo=timezone.utc)
    return context


@pytest.fixture
def valid_input():
    return {
        "pipeline_run": {
            "id": "test-run-id",
            "customer_id": "cust-123",
            "pipeline_type": "invoice-processing",
            "status": "pending",
            "created_at": "2023-01-01T00:00:00Z",
        },
        "source_blob": "uploads/cust-123/invoice.pdf",
    }


def test_orchestrator_happy_path(mock_context, valid_input):
    mock_context.get_input.return_value = valid_input

    # Mock activity results
    ocr_success = {
        "status": "completed",
        "artifacts": ["ocr-1"],
    }
    validation_success = {
        "status": "completed",
        "validation_status": "valid",
        "artifacts": ["val-1"],
    }
    publish_success = {"status": "completed"}

    gen = pipeline_orchestrator(mock_context)

    # 1. Update status to 'running'
    next(gen)
    assert (
        mock_context.call_activity.call_args_list[0][0][0]
        == "update_pipeline_run_status"
    )
    assert mock_context.call_activity.call_args_list[0][0][1]["status"] == "running"

    # 2. OCR Step
    gen.send(None)
    assert (
        mock_context.call_activity.call_args_list[1][0][0]
        == "ocr_document_intelligence"
    )

    # 3. Validation Step
    gen.send(ocr_success)
    assert (
        mock_context.call_activity.call_args_list[2][0][0] == "field_validation_worker"
    )

    # 4. Publication Step
    gen.send(validation_success)
    assert (
        mock_context.call_activity.call_args_list[3][0][0] == "final_result_publisher"
    )

    # 5. Finalize status to 'completed'
    gen.send(publish_success)
    assert (
        mock_context.call_activity.call_args_list[4][0][0]
        == "update_pipeline_run_status"
    )
    assert mock_context.call_activity.call_args_list[4][0][1]["status"] == "completed"

    # End of orchestrator
    with pytest.raises(StopIteration) as exc:
        gen.send(None)
    assert exc.value.value == "completed"


def test_orchestrator_ocr_failure(mock_context, valid_input):
    mock_context.get_input.return_value = valid_input

    ocr_failure = {
        "status": "failed",
        "friendly_error": "Document is blurry.",
    }

    gen = pipeline_orchestrator(mock_context)

    # 1. Start
    next(gen)

    # 2. OCR Step
    gen.send(None)

    # 3. Handle OCR failure and update status to 'failed'
    gen.send(ocr_failure)
    assert (
        mock_context.call_activity.call_args_list[2][0][0]
        == "update_pipeline_run_status"
    )
    assert mock_context.call_activity.call_args_list[2][0][1]["status"] == "failed"
    assert (
        "blurry"
        not in mock_context.call_activity.call_args_list[2][0][1]["friendly_error"]
    )
    # Actually, in my implementation I used a generic error message for the catch-all,
    # but for specific step failures I should check what I did.
    # In orchestrator.py: raise Exception(ocr_result.get("friendly_error") or "OCR step failed.")
    # Then caught by except Exception as e: ... friendly_error: "An error occurred during document processing. ..."

    assert (
        "An error occurred"
        in mock_context.call_activity.call_args_list[2][0][1]["friendly_error"]
    )

    with pytest.raises(StopIteration) as exc:
        gen.send(None)
    assert exc.value.value == "failed"


def test_orchestrator_safety_boundary(mock_context, valid_input):
    """
    Ensure that even if an activity returns sensitive data in an error,
    the orchestrator redacts it for the customer status.
    """
    mock_context.get_input.return_value = valid_input

    ocr_unsafe_failure = {
        "status": "failed",
        "friendly_error": "Failed to connect to https://secret-endpoint.azure.com with key=12345",
    }

    gen = pipeline_orchestrator(mock_context)
    next(gen)  # 'running'
    gen.send(None)  # OCR call

    # Send unsafe failure
    gen.send(ocr_unsafe_failure)

    # Check last call to update_pipeline_run_status
    last_call_args = mock_context.call_activity.call_args_list[-1][0][1]
    assert last_call_args["status"] == "failed"
    assert "secret-endpoint" not in last_call_args["friendly_error"]
    assert "12345" not in last_call_args["friendly_error"]
    assert "An error occurred" in last_call_args["friendly_error"]


def test_activities_basic():
    # Simple smokes tests for activities
    assert update_pipeline_run_status({"id": "1", "status": "running"}) is True

    ocr = ocr_document_intelligence({"run_id": "1"})
    assert ocr["status"] == "completed"
    assert "ocr-result-artifact-id" in ocr["artifacts"]

    val = field_validation_worker({"run_id": "1"})
    assert val["status"] == "completed"
    assert val["validation_status"] == "valid"

    pub = final_result_publisher({"run_id": "1"})
    assert pub["status"] == "completed"
    assert pub["publication_status"] == "published"
