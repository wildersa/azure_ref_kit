import json
import unittest
from unittest.mock import patch, MagicMock

from pydantic import ValidationError
from building_blocks.mcp.devops_status_adapter.src.adapter import DevOpsStatusAdapter
from building_blocks.mcp.devops_mcp_tool_contract.src.models import (
    GetPipelineRunStatusResponse,
    ListRecentPipelineRunsResponse,
    PipelineStatus,
    PipelineResult,
)

class TestDevOpsStatusAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token"
        )

    def test_transport_injection(self):
        mock_transport = MagicMock()
        mock_transport.return_value = (b'{"id": 1}', 200)

        adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token",
            transport=mock_transport
        )

        adapter._make_request("https://dev.azure.com/test-org/test-project/_apis/build/builds/1")
        mock_transport.assert_called_once()

    def test_rejected_non_azure_devops_hosts(self):
        with self.assertRaisesRegex(ValueError, "only dev.azure.com is allowed"):
            DevOpsStatusAdapter(
                organization_url="https://evil.com/org",
                project="test-project",
                token="test-token"
            )

    @patch("building_blocks.mcp.devops_status_adapter.src.adapter.logger")
    def test_sanitized_failure_logging(self, mock_logger):
        mock_transport = MagicMock()
        mock_transport.side_effect = Exception("Sensitive technical error info")

        adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token",
            transport=mock_transport
        )

        with self.assertRaises(RuntimeError):
            adapter._make_request("https://dev.azure.com/test-org/test-project/_apis/build/builds/1")

        # Verify that the sensitive error info is NOT logged
        for call in mock_logger.error.call_args_list:
            self.assertNotIn("Sensitive technical error info", call[0][0])

    def test_rejected_unsafe_identifiers_in_get_status(self):
        # Test that the public method rejects unsafe identifiers
        with self.assertRaises(ValidationError):
            self.adapter.get_pipeline_run_status(pipeline_id="invalid/id", run_id="123")
        with self.assertRaises(ValidationError):
            self.adapter.get_pipeline_run_status(pipeline_id="123", run_id="invalid:id")

    def test_rejected_unsafe_identifiers_in_list_runs(self):
        # Test that the public method rejects unsafe identifiers
        with self.assertRaises(ValidationError):
            self.adapter.list_recent_pipeline_runs(pipeline_id="invalid/id")
        with self.assertRaises(ValidationError):
            self.adapter.list_recent_pipeline_runs(pipeline_id="123", branch="invalid:branch")

    def test_rejected_out_of_bounds_top(self):
        with self.assertRaisesRegex(ValueError, "top must be between 1 and 20"):
            self.adapter.list_recent_pipeline_runs(pipeline_id="123", top=0)
        with self.assertRaisesRegex(ValueError, "top must be between 1 and 20"):
            self.adapter.list_recent_pipeline_runs(pipeline_id="123", top=21)

    def test_get_pipeline_run_status_success(self):
        mock_response_data = {
            "id": 12345,
            "status": "completed",
            "result": "succeeded",
            "sourceBranch": "refs/heads/main",
            "sourceVersion": "a1b2c3d4e5f6g7h8",
            "startTime": "2024-01-01T10:00:00Z",
            "finishTime": "2024-01-01T10:05:00Z",
            "buildNumber": "20240101.1",
            "definition": {"name": "Test Pipeline"},
            "_links": {"web": {"href": "https://dev.azure.com/test-org/test-project/_build/results?buildId=12345"}}
        }

        mock_transport = MagicMock()
        mock_transport.return_value = (json.dumps(mock_response_data).encode("utf-8"), 200)

        adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token",
            transport=mock_transport
        )

        response = adapter.get_pipeline_run_status(pipeline_id="123", run_id="12345")

        self.assertIsInstance(response, GetPipelineRunStatusResponse)
        self.assertEqual(response.pipeline_name, "Test Pipeline")
        self.assertEqual(response.run_id, "12345")
        self.assertEqual(response.status, PipelineStatus.COMPLETED)
        self.assertEqual(response.result, PipelineResult.SUCCEEDED)
        self.assertEqual(response.branch, "refs/heads/main")
        self.assertEqual(response.commit_sha, "a1b2c3d")
        self.assertEqual(response.duration_seconds, 300)
        self.assertEqual(str(response.portal_url), "https://dev.azure.com/test-org/test-project/_build/results?buildId=12345")

    def test_list_recent_pipeline_runs_success(self):
        mock_response_data = {
            "count": 2,
            "value": [
                {
                    "id": 12346,
                    "status": "completed",
                    "result": "succeeded",
                    "sourceBranch": "refs/heads/main",
                    "startTime": "2024-01-02T10:00:00Z",
                    "definition": {"name": "Test Pipeline"}
                },
                {
                    "id": 12345,
                    "status": "completed",
                    "result": "failed",
                    "sourceBranch": "refs/heads/main",
                    "startTime": "2024-01-01T10:00:00Z",
                    "definition": {"name": "Test Pipeline"}
                }
            ]
        }

        mock_transport = MagicMock()
        mock_transport.return_value = (json.dumps(mock_response_data).encode("utf-8"), 200)

        adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token",
            transport=mock_transport
        )

        response = adapter.list_recent_pipeline_runs(pipeline_id="123", top=2)

        self.assertIsInstance(response, ListRecentPipelineRunsResponse)
        self.assertEqual(response.pipeline_name, "Test Pipeline")
        self.assertEqual(len(response.runs), 2)
        self.assertEqual(response.runs[0].run_id, "12346")
        self.assertEqual(response.runs[1].result, PipelineResult.FAILED)

    def test_malformed_provider_payload_fails_closed(self):
        mock_response_data = {
            "id": 12345,
            "definition": {"name": "Test Pipeline"}
        }

        mock_transport = MagicMock()
        mock_transport.return_value = (json.dumps(mock_response_data).encode("utf-8"), 200)

        adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token",
            transport=mock_transport
        )

        with self.assertRaisesRegex(RuntimeError, "Malformed provider response."):
            adapter.get_pipeline_run_status(pipeline_id="123", run_id="12345")

    def test_api_error_fails_closed(self):
        mock_transport = MagicMock()
        mock_transport.return_value = (b"", 404)

        adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token",
            transport=mock_transport
        )

        with self.assertRaisesRegex(RuntimeError, "Internal error fetching DevOps status."):
            adapter.get_pipeline_run_status(pipeline_id="123", run_id="nonexistent")

    def test_credential_safety_in_headers(self):
        headers = self.adapter._get_headers()
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Basic "))
        # Ensure token is not present in plain text
        self.assertNotIn("test-token", headers["Authorization"])

    def test_list_recent_pipeline_runs_pagination_and_branch(self):
        mock_transport = MagicMock()
        mock_transport.return_value = (
            json.dumps({"count": 0, "value": []}).encode("utf-8"),
            200,
        )

        adapter = DevOpsStatusAdapter(
            organization_url="https://dev.azure.com/test-org",
            project="test-project",
            token="test-token",
            transport=mock_transport,
        )

        adapter.list_recent_pipeline_runs(pipeline_id="123", branch="feat-branch", top=10)

        args, kwargs = mock_transport.call_args
        request = args[0]
        self.assertIn("%24top=10", request.full_url)
        self.assertIn("branchName=feat-branch", request.full_url)

if __name__ == "__main__":
    unittest.main()
