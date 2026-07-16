import pytest
import sys
import os
import logging
from unittest.mock import MagicMock
import azure.functions as func
import azure.durable_functions as df
from datetime import datetime, timezone

# Add parent directory to sys.path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the orchestrator and activities
from function_app import http_start, blob_start
from src.orchestrator import pipeline_orchestrator
from src.activities import (
    update_pipeline_run_status,
    update_pipeline_step_status,
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

    # 1. Update overall status to 'running'
    next(gen)
    assert (
        mock_context.call_activity.call_args_list[0][0][0]
        == "update_pipeline_run_status"
    )
    assert (
        mock_context.call_activity.call_args_list[0][0][1]["correlation_id"]
        == "test-run-id"
    )

    # 2. Start OCR step
    gen.send(None)
    assert (
        mock_context.call_activity.call_args_list[1][0][0]
        == "update_pipeline_step_status"
    )
    assert (
        mock_context.call_activity.call_args_list[1][0][1]["name"]
        == "ocr-document-intelligence"
    )
    assert mock_context.call_activity.call_args_list[1][0][1]["status"] == "running"

    # 3. OCR Step (with retry)
    gen.send(None)
    assert (
        mock_context.call_activity_with_retry.call_args_list[0][0][0]
        == "ocr_document_intelligence"
    )
    assert (
        mock_context.call_activity_with_retry.call_args_list[0][0][2]["source_blob"]
        == valid_input["source_blob"]
    )

    # 4. Complete OCR step
    gen.send(ocr_success)
    assert (
        mock_context.call_activity.call_args_list[2][0][0]
        == "update_pipeline_step_status"
    )
    assert mock_context.call_activity.call_args_list[2][0][1]["status"] == "completed"

    # 5. Start Validation step
    gen.send(None)
    assert (
        mock_context.call_activity.call_args_list[3][0][0]
        == "update_pipeline_step_status"
    )
    assert (
        mock_context.call_activity.call_args_list[3][0][1]["name"]
        == "field-validation-worker"
    )

    # 6. Validation Step (direct call)
    gen.send(None)
    assert (
        mock_context.call_activity.call_args_list[4][0][0] == "field_validation_worker"
    )

    # 7. Complete Validation step
    gen.send(validation_success)
    assert (
        mock_context.call_activity.call_args_list[5][0][0]
        == "update_pipeline_step_status"
    )
    assert mock_context.call_activity.call_args_list[5][0][1]["status"] == "completed"

    # 8. Start Publication step
    gen.send(None)
    assert (
        mock_context.call_activity.call_args_list[6][0][0]
        == "update_pipeline_step_status"
    )
    assert (
        mock_context.call_activity.call_args_list[6][0][1]["name"]
        == "final-result-publisher"
    )

    # 9. Publication Step (with retry)
    gen.send(None)
    assert (
        mock_context.call_activity_with_retry.call_args_list[1][0][0]
        == "final_result_publisher"
    )

    # 10. Complete Publication step
    gen.send(publish_success)
    assert (
        mock_context.call_activity.call_args_list[7][0][0]
        == "update_pipeline_step_status"
    )
    assert mock_context.call_activity.call_args_list[7][0][1]["status"] == "completed"

    # 11. Finalize overall status to 'completed'
    gen.send(None)
    assert (
        mock_context.call_activity.call_args_list[8][0][0]
        == "update_pipeline_run_status"
    )
    assert mock_context.call_activity.call_args_list[8][0][1]["status"] == "completed"
    assert (
        mock_context.call_activity.call_args_list[8][0][1]["correlation_id"]
        == "test-run-id"
    )

    # End of orchestrator
    with pytest.raises(StopIteration) as exc:
        gen.send(None)
    assert exc.value.value["status"] == "completed"
    assert "ocr-1" in exc.value.value["artifacts"]
    assert "val-1" in exc.value.value["artifacts"]


def test_orchestrator_ocr_failure(mock_context, valid_input):
    mock_context.get_input.return_value = valid_input

    ocr_failure = {
        "status": "failed",
        "friendly_error": "Document is blurry.",
    }

    gen = pipeline_orchestrator(mock_context)

    # 1. Start overall
    next(gen)

    # 2. Start OCR step
    gen.send(None)

    # 3. OCR call
    gen.send(None)

    # 4. Send failure (raises ValueError in orchestrator)
    gen.send(ocr_failure)

    # 5. Move to second yield in except block
    gen.send(None)

    # Should update step status to 'failed'
    assert (
        mock_context.call_activity.call_args_list[2][0][0]
        == "update_pipeline_step_status"
    )
    assert mock_context.call_activity.call_args_list[2][0][1]["status"] == "failed"

    # Should update overall status to 'failed'
    assert (
        mock_context.call_activity.call_args_list[3][0][0]
        == "update_pipeline_run_status"
    )
    assert mock_context.call_activity.call_args_list[3][0][1]["status"] == "failed"
    assert (
        mock_context.call_activity.call_args_list[3][0][1]["correlation_id"]
        == "test-run-id"
    )
    assert (
        "blurry"
        not in mock_context.call_activity.call_args_list[2][0][1]["friendly_error"]
    )
    assert (
        "blurry"
        not in mock_context.call_activity.call_args_list[3][0][1]["friendly_error"]
    )

    assert (
        "An error occurred"
        in mock_context.call_activity.call_args_list[3][0][1]["friendly_error"]
    )

    with pytest.raises(StopIteration) as exc:
        gen.send(None)
    assert exc.value.value["status"] == "failed"


def test_orchestrator_invalid_contract(mock_context):
    invalid_input = {
        "pipeline_run": {
            "id": "missing-fields"
            # Missing customer_id, pipeline_type, created_at, status
        }
    }
    mock_context.get_input.return_value = invalid_input

    gen = pipeline_orchestrator(mock_context)
    with pytest.raises(StopIteration) as exc:
        next(gen)
    assert exc.value.value["status"] == "failed"
    assert "Contract validation failed" in exc.value.value["error"]


def test_orchestrator_safety_boundary(mock_context, valid_input, caplog):
    """
    Ensure that even if an activity returns sensitive data in an error,
    the orchestrator redacts it for both the customer status AND internal logs.
    """
    mock_context.get_input.return_value = valid_input

    ocr_unsafe_failure = {
        "status": "failed",
        "friendly_error": "Failed to connect to https://secret-endpoint.azure.com with key=12345",
    }

    gen = pipeline_orchestrator(mock_context)
    next(gen)  # 'running'
    gen.send(None)  # OCR Step Start
    gen.send(None)  # OCR call (with retry)

    # Send unsafe failure (raises ValueError in orchestrator)
    gen.send(ocr_unsafe_failure)

    # Move to second yield in except block
    gen.send(None)

    try:
        gen.send(None)
    except StopIteration:
        pass

    # 1. Check customer-facing status (must be redacted)
    # The last call is to update_pipeline_run_status
    last_run_status_call = [
        c
        for c in mock_context.call_activity.call_args_list
        if c[0][0] == "update_pipeline_run_status"
    ][-1]
    last_run_args = last_run_status_call[0][1]
    assert last_run_args["status"] == "failed"
    assert "secret-endpoint" not in last_run_args["friendly_error"]
    assert "12345" not in last_run_args["friendly_error"]
    assert "An error occurred" in last_run_args["friendly_error"]

    # Check step status (must also be redacted)
    last_step_status_call = [
        c
        for c in mock_context.call_activity.call_args_list
        if c[0][0] == "update_pipeline_step_status"
    ][-1]
    last_step_args = last_step_status_call[0][1]
    assert last_step_args["status"] == "failed"
    assert "secret-endpoint" not in last_step_args["friendly_error"]
    assert "12345" not in last_step_args["friendly_error"]

    # 2. Check internal logs (must NOT contain the sensitive error text or run_id)
    assert "secret-endpoint" not in caplog.text
    assert "12345" not in caplog.text
    assert "test-run-id" not in caplog.text
    assert "Pipeline execution failed" in caplog.text


def test_http_start_logging_safety(caplog):
    """
    Verify that http_start does not log the instance_id.
    """
    caplog.set_level(logging.INFO)
    req = MagicMock(spec=func.HttpRequest)
    req.route_params = {"functionName": "pipeline_orchestrator"}
    req.get_json.return_value = {"pipeline_run": {"id": "test-run-id"}}

    # Mock start_new to be an async function returning a string
    async def mock_start_new(function_name, client_input=None):
        return "test-instance-id"

    client = MagicMock(spec=df.DurableOrchestrationClient)
    client.start_new = mock_start_new

    # We need to run the async function
    import asyncio

    # Access the original function behind the Azure Functions decorators
    func_to_call = http_start
    while True:
        if hasattr(func_to_call, "_function") and hasattr(
            func_to_call._function, "_func"
        ):
            func_to_call = func_to_call._function._func
        elif hasattr(func_to_call, "__wrapped__"):
            func_to_call = func_to_call.__wrapped__
        else:
            break

    asyncio.run(func_to_call(req, client))

    assert "test-instance-id" not in caplog.text
    assert "Orchestration started" in caplog.text


def test_activities_logging_safety(caplog):
    """
    Verify that activities do not log the run_id or status.
    """
    caplog.set_level(logging.INFO)
    run_id = "test-run-id-123"

    # 1. update_pipeline_run_status
    caplog.clear()
    update_pipeline_run_status({"id": run_id, "status": "running"})
    assert run_id not in caplog.text
    assert "running" not in caplog.text
    assert "Activity: Updating pipeline run status" in caplog.text

    # 2. update_pipeline_step_status
    caplog.clear()
    update_pipeline_step_status(
        {"run_id": run_id, "status": "running", "name": "step1"}
    )
    assert run_id not in caplog.text
    assert "Activity: Updating pipeline step status" in caplog.text

    # 3. ocr_document_intelligence
    caplog.clear()
    ocr_document_intelligence({"run_id": run_id})
    assert run_id not in caplog.text
    assert "Activity: Starting OCR process" in caplog.text

    # 3. field_validation_worker
    caplog.clear()
    field_validation_worker({"run_id": run_id})
    assert run_id not in caplog.text
    assert "Activity: Starting field validation" in caplog.text

    # 4. final_result_publisher
    caplog.clear()
    final_result_publisher({"run_id": run_id})
    assert run_id not in caplog.text
    assert "Activity: Finalizing publication" in caplog.text


def test_activities_basic():
    # Simple smokes tests for activities
    assert update_pipeline_run_status({"id": "1", "status": "running"}) is True
    assert (
        update_pipeline_step_status({"run_id": "1", "status": "running", "name": "ocr"})
        is True
    )

    ocr = ocr_document_intelligence({"run_id": "1"})
    assert ocr["status"] == "completed"
    assert "ocr-result-artifact-id" in ocr["artifacts"]

    val = field_validation_worker({"run_id": "1"})
    assert val["status"] == "completed"
    assert val["validation_status"] == "valid"

    pub = final_result_publisher({"run_id": "1"})
    assert pub["status"] == "completed"
    assert pub["publication_status"] == "published"


def test_orchestrator_retry_exhaustion(mock_context, valid_input):
    """
    Verify orchestrator behavior when a retryable activity fails repeatedly.
    In Durable Functions, if call_activity_with_retry exhausts retries, it raises an exception.
    """
    mock_context.get_input.return_value = valid_input

    gen = pipeline_orchestrator(mock_context)

    # 1. Start overall
    next(gen)

    # 2. Start OCR Step
    gen.send(None)

    # 3. OCR Step (with retry)
    gen.send(None)

    # Simulate exception from call_activity_with_retry after retries exhausted
    gen.throw(Exception("Retry attempts exhausted."))

    # Move to second yield in except block
    gen.send(None)

    try:
        gen.send(None)
    except StopIteration:
        pass

    # 4. Handle failure and update status to 'failed'
    # Last call is to update_pipeline_run_status
    last_run_status_call = [
        c
        for c in mock_context.call_activity.call_args_list
        if c[0][0] == "update_pipeline_run_status"
    ][-1]
    assert last_run_status_call[0][1]["status"] == "failed"
    assert "An error occurred" in last_run_status_call[0][1]["friendly_error"]


def test_orchestrator_validation_failure_no_retry(mock_context, valid_input):
    """
    Verify that validation failure (non-retryable) immediately fails the pipeline.
    """
    mock_context.get_input.return_value = valid_input

    ocr_success = {"status": "completed", "artifacts": ["ocr-1"]}
    validation_failure = {
        "status": "failed",
        "friendly_error": "Missing mandatory field.",
    }

    gen = pipeline_orchestrator(mock_context)

    # Run through to validation
    next(gen)  # overall running
    gen.send(None)  # ocr running
    gen.send(None)  # ocr activity
    gen.send(ocr_success)  # ocr completed
    gen.send(None)  # val running
    gen.send(None)  # val activity

    # 4. Handle validation failure
    gen.send(validation_failure)

    # Move to second yield in except block
    gen.send(None)

    try:
        gen.send(None)
    except StopIteration:
        pass

    # Last call is to update_pipeline_run_status
    last_run_status_call = [
        c
        for c in mock_context.call_activity.call_args_list
        if c[0][0] == "update_pipeline_run_status"
    ][-1]
    assert last_run_status_call[0][1]["status"] == "failed"


def test_orchestrator_determinism_no_file_io(mock_context, valid_input):
    """
    Verify that the orchestrator does not perform any filesystem I/O during execution.
    This is a strict Durable Functions constraint for determinism and replay safety.
    """
    mock_context.get_input.return_value = valid_input

    from unittest.mock import patch

    # Mock 'open' to raise an error if called during orchestration
    with patch(
        "builtins.open",
        side_effect=IOError("Filesystem access forbidden during orchestration"),
    ):
        gen = pipeline_orchestrator(mock_context)
        # Run through the orchestration (triggering the first yield)
        next(gen)

    # If we reached here without an IOError, the orchestrator did not call open()
    assert (
        mock_context.call_activity.call_args_list[0][0][0]
        == "update_pipeline_run_status"
    )


def test_blob_start_logic(caplog):
    """
    Verify the logic of blob_start and ensure sensitive data is not logged.
    """
    import asyncio

    caplog.set_level(logging.INFO)

    myblob = MagicMock(spec=func.InputStream)
    blob_path = "uploads/sensitive-invoice-id.pdf"
    myblob.name = blob_path

    async def mock_start_new(function_name, client_input=None):
        assert function_name == "pipeline_orchestrator"
        assert client_input["source_blob"] == blob_path
        assert client_input["pipeline_run"]["customer_id"] == "auto-triggered"
        return "test-id"

    client = MagicMock(spec=df.DurableOrchestrationClient)
    client.start_new = mock_start_new

    # Unwrap if decorated (as in previous http_start test)
    func_to_call = blob_start
    while True:
        if hasattr(func_to_call, "_function") and hasattr(
            func_to_call._function, "_func"
        ):
            func_to_call = func_to_call._function._func
        elif hasattr(func_to_call, "__wrapped__"):
            func_to_call = func_to_call.__wrapped__
        else:
            break

    asyncio.run(func_to_call(myblob, client))

    # Regression check: blob name must not be in logs
    assert blob_path not in caplog.text
    assert "sensitive-invoice-id" not in caplog.text
    assert "Blob trigger started" in caplog.text
    assert "Orchestration started via blob trigger" in caplog.text
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
