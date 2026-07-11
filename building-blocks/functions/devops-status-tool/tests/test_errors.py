import pytest
from unittest.mock import MagicMock
from src.tool import get_build_status


@pytest.fixture
def mock_client():
    return MagicMock()


def test_api_404_handling(mock_client):
    mock_client.get_build.side_effect = ValueError("Build not found.")

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 999,
    }

    with pytest.raises(ValueError, match="Build not found."):
        get_build_status(request_params, mock_client)


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
