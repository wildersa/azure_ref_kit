import pytest
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock
from src.client import DevOpsClient


def test_get_build_url_encoding():
    client = DevOpsClient(pat="fake-pat")

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'{"id": 123}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client.get_build("https://dev.azure.com/org", "Project With Spaces", 123)

        # Verify encoded URL
        args, _ = mock_urlopen.call_args
        request = args[0]
        assert "Project%20With%20Spaces" in request.full_url
        assert " " not in request.full_url


def test_get_build_http_error():
    client = DevOpsClient(pat="fake-pat")

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test.com", code=404, msg="Not Found", hdrs={}, fp=None
        )

        with pytest.raises(ValueError, match="Build not found."):
            client.get_build("https://dev.azure.com/org", "proj", 123)


def test_get_build_auth_error():
    client = DevOpsClient(pat="fake-pat")

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test.com", code=401, msg="Unauthorized", hdrs={}, fp=None
        )

        with pytest.raises(PermissionError, match="Authentication failed."):
            client.get_build("https://dev.azure.com/org", "proj", 123)
