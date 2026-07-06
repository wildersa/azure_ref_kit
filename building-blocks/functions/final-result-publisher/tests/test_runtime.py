import pytest
from unittest.mock import MagicMock
from src.worker import publish_final_result
from src.adapters import ArtifactStoreAdapter, StatusStoreAdapter


@pytest.fixture
def mock_artifact_adapter():
    return MagicMock(spec=ArtifactStoreAdapter)


@pytest.fixture
def mock_status_adapter():
    return MagicMock(spec=StatusStoreAdapter)


def test_publish_final_result_success(mock_artifact_adapter, mock_status_adapter):
    # Arrange
    run_id = "test-run-123"
    artifact_ids = ["art-1", "art-2"]
    validation_status = "valid"

    # Act
    result = publish_final_result(
        run_id=run_id,
        validation_status=validation_status,
        artifact_ids=artifact_ids,
        artifact_adapter=mock_artifact_adapter,
        status_adapter=mock_status_adapter,
    )

    # Assert
    assert result["publication_status"] == "published"
    assert result["status"] == "completed"
    assert "business_summary" in result
    assert mock_artifact_adapter.set_visible.call_count == 2
    mock_status_adapter.update_run_status.assert_called_once()

    # Verify business summary content (customer-safe)
    assert "available" in result["business_summary"]


def test_publish_final_result_validation_failed(
    mock_artifact_adapter, mock_status_adapter
):
    # Arrange
    run_id = "test-run-123"
    artifact_ids = ["art-1"]
    validation_status = "failed"

    # Act
    result = publish_final_result(
        run_id=run_id,
        validation_status=validation_status,
        artifact_ids=artifact_ids,
        artifact_adapter=mock_artifact_adapter,
        status_adapter=mock_status_adapter,
    )

    # Assert
    assert result["status"] == "failed"
    assert "failed" in result["business_summary"]
    mock_status_adapter.update_run_status.assert_called_with(
        run_id=run_id,
        status="failed",
        business_summary=result["business_summary"],
        finished_at=result["finished_at"],
    )


def test_publish_final_result_artifact_error(
    mock_artifact_adapter, mock_status_adapter
):
    # Arrange
    run_id = "test-run-123"
    artifact_ids = ["art-1"]
    mock_artifact_adapter.set_visible.side_effect = Exception("Storage error")

    # Act
    result = publish_final_result(
        run_id=run_id,
        validation_status="valid",
        artifact_ids=artifact_ids,
        artifact_adapter=mock_artifact_adapter,
        status_adapter=mock_status_adapter,
    )

    # Assert
    assert result["publication_status"] == "failed"
    assert "internal error" in result["friendly_error"].lower()
    # Ensure no technical error message leaked
    assert "Storage error" not in result["friendly_error"]


def test_safety_boundary_no_leakage(mock_artifact_adapter, mock_status_adapter):
    # Arrange
    run_id = "test-run-123"
    # Input containing potentially unsafe technical data

    # Act
    # We pass standard inputs, but we want to ensure the result doesn't somehow pick up
    # and return unexpected fields if they were to be passed (though our function signature prevents it).
    # More importantly, we check that the business_summary and friendly_error are clean.
    result = publish_final_result(
        run_id=run_id,
        validation_status="valid",
        artifact_ids=[],
        artifact_adapter=mock_artifact_adapter,
        status_adapter=mock_status_adapter,
    )

    # Assert
    result_str = str(result)
    assert "secret123" not in result_str
    assert "internal" not in result_str
    assert "raw_ocr" not in result_str


def test_idempotency_behavior(mock_artifact_adapter, mock_status_adapter):
    # Arrange
    run_id = "test-run-123"
    artifact_ids = ["art-1"]

    # Act - Call twice
    res1 = publish_final_result(
        run_id, "valid", artifact_ids, mock_artifact_adapter, mock_status_adapter
    )
    res2 = publish_final_result(
        run_id, "valid", artifact_ids, mock_artifact_adapter, mock_status_adapter
    )

    # Assert
    assert res1["publication_status"] == "published"
    assert res2["publication_status"] == "published"
    assert mock_artifact_adapter.set_visible.call_count == 2
    assert mock_status_adapter.update_run_status.call_count == 2


def test_log_safety_boundary_on_exception(
    mock_artifact_adapter, mock_status_adapter, caplog
):
    # Arrange
    run_id = "test-run-123"
    artifact_ids = ["artifact-xyz-789"]  # Raw artifact ID
    # Mock an exception that contains technical details like a storage URL and SAS token
    mock_artifact_adapter.set_visible.side_effect = Exception(
        "Access denied to https://account.blob.core.windows.net/container/blob?sv=2019-12-12&ss=b&srt=o&sp=rwdlacix&se=2021-01-01T00:00:00Z&st=2021-01-01T00:00:00Z&spr=https&sig=secret"
    )

    # Act
    publish_final_result(
        run_id=run_id,
        validation_status="valid",
        artifact_ids=artifact_ids,
        artifact_adapter=mock_artifact_adapter,
        status_adapter=mock_status_adapter,
    )

    # Assert
    log_text = caplog.text
    # Verify that the technical details are NOT in the logs
    assert "https://account.blob.core.windows.net" not in log_text
    assert "sv=2019-12-12" not in log_text
    assert "sig=secret" not in log_text
    # Verify that raw artifact IDs are NOT in the logs
    assert "artifact-xyz-789" not in log_text
    # Verify that the run_id IS in the logs for correlation
    assert run_id in log_text
    # Verify that a safe message is logged instead
    assert "Failed to set visibility for one or more artifacts" in log_text
