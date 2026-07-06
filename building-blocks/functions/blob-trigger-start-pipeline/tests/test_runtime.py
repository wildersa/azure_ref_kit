import pytest
import azure.functions as func
import azure.durable_functions as df
from unittest.mock import AsyncMock, MagicMock, patch
from function_app import main_logic


@pytest.mark.asyncio
async def test_blob_trigger_success():
    # Arrange
    mock_blob = MagicMock(spec=func.InputStream)
    mock_blob.name = "uploads/customer123/invoice.pdf"
    mock_blob.length = 1024
    mock_blob.metadata = {"document_type": "invoice", "correlation_id": "corr-456"}

    mock_client = MagicMock(spec=df.DurableOrchestrationClient)
    mock_client.start_new = AsyncMock(return_value="instance-id-123")

    # Act
    await main_logic(mock_blob, mock_client)

    # Assert
    mock_client.start_new.assert_called_once()
    args, kwargs = mock_client.start_new.call_args

    orchestrator_name = args[0]
    orchestration_input = kwargs["client_input"]
    payload = orchestration_input["pipeline_run"]
    source_blob = orchestration_input["source_blob"]
    instance_id = kwargs["instance_id"]

    assert orchestrator_name == "pipeline_orchestrator"
    assert source_blob == "uploads/customer123/invoice.pdf"
    assert payload["customer_id"] == "customer123"
    assert payload["pipeline_type"] == "invoice"
    assert payload["correlation_id"] == "corr-456"
    assert payload["status"] == "pending"
    assert payload["id"] == instance_id
    # Ensure no secrets or raw URLs in payload
    assert "url" not in payload
    assert "connection" not in payload


@pytest.mark.asyncio
async def test_blob_trigger_missing_metadata():
    # Arrange
    mock_blob = MagicMock(spec=func.InputStream)
    mock_blob.name = "uploads/invalid/file.pdf"
    mock_blob.metadata = {}  # Missing document_type

    mock_client = MagicMock(spec=df.DurableOrchestrationClient)
    mock_client.start_new = AsyncMock()

    # Act
    await main_logic(mock_blob, mock_client)

    # Assert
    mock_client.start_new.assert_not_called()


@pytest.mark.asyncio
async def test_blob_trigger_prefer_metadata_over_path():
    # Arrange
    mock_blob = MagicMock(spec=func.InputStream)
    mock_blob.name = "uploads/path-customer/file.pdf"
    mock_blob.metadata = {
        "customer_id": "metadata-customer",
        "document_type": "receipt",
    }

    mock_client = MagicMock(spec=df.DurableOrchestrationClient)
    mock_client.start_new = AsyncMock(return_value="instance-id-789")

    # Act
    await main_logic(mock_blob, mock_client)

    # Assert
    mock_client.start_new.assert_called_once()
    _, kwargs = mock_client.start_new.call_args
    payload = kwargs["client_input"]["pipeline_run"]
    assert payload["customer_id"] == "metadata-customer"


@pytest.mark.asyncio
async def test_blob_trigger_validation_failure():
    # Arrange
    mock_blob = MagicMock(spec=func.InputStream)
    mock_blob.name = "uploads/customer123/invoice.pdf"
    mock_blob.length = 1024
    mock_blob.metadata = {"document_type": "invoice", "correlation_id": "corr-456"}

    mock_client = MagicMock(spec=df.DurableOrchestrationClient)
    mock_client.start_new = AsyncMock()

    # Mock jsonschema.validate to raise an error
    with patch("jsonschema.validate") as mock_validate:
        import jsonschema

        mock_validate.side_effect = jsonschema.ValidationError("Invalid payload")

        # Act
        await main_logic(mock_blob, mock_client)

        # Assert
        mock_client.start_new.assert_not_called()
