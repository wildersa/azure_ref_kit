import pytest
import logging
from unittest.mock import MagicMock
from src.tool import get_build_status


@pytest.fixture
def mock_client():
    return MagicMock()


def test_validation_log_redaction(mock_client, caplog):
    caplog.set_level(logging.WARNING)

    # organization_url is sensitive (internal identifier)
    request_params = {
        "organization_url": "https://malicious.com",
        "project": "proj",
        "build_id": 123,
    }

    with pytest.raises(ValueError):
        get_build_status(request_params, mock_client)

    # Verify that the malicious URL is NOT in the logs
    for record in caplog.records:
        assert "malicious.com" not in record.message
    assert (
        "Build status request failed due to validation or missing data." in caplog.text
    )


def test_mapping_error_log_redaction(mock_client, caplog):
    caplog.set_level(logging.WARNING)

    # Mocking an unexpected error during mapping (e.g. malformed raw_build missing portal_url)
    mock_client.get_build.return_value = {"id": 123, "status": "completed"}

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 123,
    }

    # This will raise ValueError because portal_url is missing
    with pytest.raises(ValueError):
        get_build_status(request_params, mock_client)

    # Verify log message is safe
    assert (
        "Build status request failed due to validation or missing data." in caplog.text
    )


def test_unexpected_error_log_redaction(mock_client, caplog):
    caplog.set_level(logging.ERROR)

    # Mocking a totally unexpected error
    mock_client.get_build.side_effect = Exception("Secret Internal Error")

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 123,
    }

    with pytest.raises(RuntimeError, match="Failed to retrieve or map build status."):
        get_build_status(request_params, mock_client)

    # Verify log message is safe
    assert "Error in get_build_status mapping." in caplog.text
    # Ensure secret error is NOT logged
    assert "Secret Internal Error" not in caplog.text


def test_api_404_handling(mock_client, caplog):
    caplog.set_level(logging.WARNING)
    mock_client.get_build.side_effect = ValueError("Build not found.")

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 999,
    }

    with pytest.raises(ValueError, match="Build not found."):
        get_build_status(request_params, mock_client)

    assert (
        "Build status request failed due to validation or missing data." in caplog.text
    )


def test_api_401_handling(mock_client):
    mock_client.get_build.side_effect = PermissionError("Authentication failed.")

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 123,
    }

    with pytest.raises(RuntimeError, match="Failed to retrieve or map build status."):
        get_build_status(request_params, mock_client)


def test_timeout_handling(mock_client):
    mock_client.get_build.side_effect = ConnectionError(
        "Failed to connect to Azure DevOps."
    )

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 123,
    }

    with pytest.raises(RuntimeError, match="Failed to retrieve or map build status."):
        get_build_status(request_params, mock_client)
