import pytest
from unittest.mock import MagicMock
from src.tool import get_build_status


@pytest.fixture
def mock_client():
    return MagicMock()


def test_validation_invalid_url(mock_client):
    request_params = {
        "organization_url": "https://malicious.com",
        "project": "proj",
        "build_id": 123,
    }
    with pytest.raises(ValueError, match="Invalid organization URL"):
        get_build_status(request_params, mock_client)


def test_validation_invalid_project(mock_client):
    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "invalid; project",
        "build_id": 123,
    }
    with pytest.raises(ValueError, match="Invalid project identifier"):
        get_build_status(request_params, mock_client)


def test_validation_invalid_build_id(mock_client):
    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": "not-an-int",
    }

    with pytest.raises(ValueError, match="Invalid request parameters."):
        get_build_status(request_params, mock_client)
