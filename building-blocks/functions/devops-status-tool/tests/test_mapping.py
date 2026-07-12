import pytest
from unittest.mock import MagicMock
from src.tool import get_build_status
from src.models import BuildStatus, BuildResult


@pytest.fixture
def mock_client():
    return MagicMock()


def test_get_build_status_success(mock_client):
    # Mock API response matching the real schema
    mock_client.get_build.return_value = {
        "id": 12345,
        "status": "completed",
        "result": "succeeded",
        "queueTime": "2026-07-03T09:59:00Z",
        "startTime": "2026-07-03T10:00:00Z",
        "finishTime": "2026-07-03T10:05:00Z",
        "definition": {"name": "Test Pipeline"},
        "sourceBranch": "refs/heads/main",  # Should be redacted
        "_links": {
            "web": {
                "href": "https://dev.azure.com/org/proj/_build/results?buildId=12345"
            }
        },
    }

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 12345,
    }

    response = get_build_status(request_params, mock_client)

    assert response.pipeline_name == "Test Pipeline"
    assert response.run_id == "12345"
    assert response.status == BuildStatus.COMPLETED
    assert response.result == BuildResult.SUCCEEDED
    assert response.branch == "redacted"
    assert response.duration_seconds == 300
    assert response.queue_time is not None
    assert str(response.portal_url).startswith("https://dev.azure.com/org/proj")


def test_get_build_status_queued(mock_client):
    # Mock API response for a queued build (no startTime yet)
    mock_client.get_build.return_value = {
        "id": 67890,
        "status": "queued",
        "result": "none",
        "queueTime": "2026-07-03T11:00:00Z",
        "startTime": None,
        "definition": {"name": "Queued Pipeline"},
        "_links": {
            "web": {
                "href": "https://dev.azure.com/org/proj/_build/results?buildId=67890"
            }
        },
    }

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "proj",
        "build_id": 67890,
    }

    response = get_build_status(request_params, mock_client)

    assert response.status == BuildStatus.QUEUED
    assert response.start_time is None
    assert response.queue_time is not None


def test_get_build_status_redaction(mock_client):
    mock_client.get_build.return_value = {
        "id": 123,
        "status": "inProgress",
        "startTime": "2026-07-03T12:00:00Z",
        "definition": {"name": "Secure Pipeline"},
        "sourceBranch": "feature/top-secret",
        "sourceVersion": "abc123def",
        "_links": {
            "web": {"href": "https://dev.azure.com/org/p/_build/results?buildId=123"}
        },
    }

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "p",
        "build_id": 123,
    }

    response = get_build_status(request_params, mock_client)

    assert response.branch == "redacted"
    # Ensure raw payload fields don't accidentally leak into summary if we use them
    assert "feature/top-secret" not in response.summary
    assert "abc123def" not in response.summary


def test_project_with_spaces(mock_client):
    mock_client.get_build.return_value = {
        "id": 456,
        "status": "completed",
        "result": "succeeded",
        "startTime": "2026-07-03T10:00:00Z",
        "definition": {"name": "Space Pipeline"},
        "_links": {
            "web": {
                "href": "https://dev.azure.com/org/Project%20With%20Spaces/_build/results?buildId=456"
            }
        },
    }

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "Project With Spaces",
        "build_id": 456,
    }

    response = get_build_status(request_params, mock_client)

    assert response.pipeline_name == "Space Pipeline"
    # Verify client was called with encoded project name
    mock_client.get_build.assert_called_once_with(
        "https://dev.azure.com/org", "Project With Spaces", 456
    )


def test_get_build_status_untrusted_portal_host(mock_client):
    mock_client.get_build.return_value = {
        "id": 123,
        "status": "completed",
        "definition": {"name": "Test"},
        "startTime": "2026-07-03T10:00:00Z",
        "_links": {
            "web": {
                "href": "https://malicious-site.com/org/p/_build/results?buildId=123"
            }
        },
    }

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "p",
        "build_id": 123,
    }

    with pytest.raises(
        ValueError, match="Provider returned a portal URL with an untrusted host."
    ):
        get_build_status(request_params, mock_client)


def test_get_build_status_non_https_portal(mock_client):
    mock_client.get_build.return_value = {
        "id": 123,
        "status": "completed",
        "definition": {"name": "Test"},
        "startTime": "2026-07-03T10:00:00Z",
        "_links": {
            "web": {"href": "http://dev.azure.com/org/p/_build/results?buildId=123"}
        },
    }

    request_params = {
        "organization_url": "https://dev.azure.com/org",
        "project": "p",
        "build_id": 123,
    }

    with pytest.raises(
        ValueError, match="Provider returned an unsafe non-HTTPS portal URL."
    ):
        get_build_status(request_params, mock_client)


def test_get_build_status_different_org_same_host(mock_client):
    mock_client.get_build.return_value = {
        "id": 123,
        "status": "completed",
        "definition": {"name": "Test"},
        "startTime": "2026-07-03T10:00:00Z",
        "_links": {
            "web": {
                "href": "https://dev.azure.com/other-org/p/_build/results?buildId=123"
            }
        },
    }

    request_params = {
        "organization_url": "https://dev.azure.com/real-org",
        "project": "p",
        "build_id": 123,
    }

    with pytest.raises(
        ValueError, match="Provider returned a portal URL for a different organization."
    ):
        get_build_status(request_params, mock_client)


def test_get_build_status_different_org_visualstudio(mock_client):
    mock_client.get_build.return_value = {
        "id": 123,
        "status": "completed",
        "definition": {"name": "Test"},
        "startTime": "2026-07-03T10:00:00Z",
        "_links": {
            "web": {
                "href": "https://other.visualstudio.com/p/_build/results?buildId=123"
            }
        },
    }

    request_params = {
        "organization_url": "https://real.visualstudio.com",
        "project": "p",
        "build_id": 123,
    }

    with pytest.raises(
        ValueError, match="Provider returned a portal URL for a different organization."
    ):
        get_build_status(request_params, mock_client)
