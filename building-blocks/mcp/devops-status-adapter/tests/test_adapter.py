import json
import unittest
from unittest.mock import patch, MagicMock

from building_blocks.mcp.devops_status_adapter.src.adapter import DevOpsStatusAdapter
from pydantic import ValidationError
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
            token="test-token",
        )

    @patch("building_blocks.mcp.devops_status_adapter.src.adapter.urlopen")
    def test_get_pipeline_run_status_success(self, mock_urlopen):
        # Mock ADO response
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
            "_links": {
                "web": {
                    "href": "https://dev.azure.com/test-org/test-project/_build/results?buildId=12345"
                }
            },
        }

        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_cm.status = 200
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        response = self.adapter.get_pipeline_run_status(
            pipeline_id="123", run_id="12345"
        )

        self.assertIsInstance(response, GetPipelineRunStatusResponse)
        self.assertEqual(response.pipeline_name, "Test Pipeline")
        self.assertEqual(response.run_id, "12345")
        self.assertEqual(response.status, PipelineStatus.COMPLETED)
        self.assertEqual(response.result, PipelineResult.SUCCEEDED)
        self.assertEqual(response.branch, "refs/heads/main")
        self.assertEqual(response.commit_sha, "a1b2c3d")
        self.assertEqual(response.duration_seconds, 300)
        self.assertEqual(
            str(response.portal_url),
            "https://dev.azure.com/test-org/test-project/_build/results?buildId=12345",
        )

    @patch("building_blocks.mcp.devops_status_adapter.src.adapter.urlopen")
    def test_list_recent_pipeline_runs_success(self, mock_urlopen):
        mock_response_data = {
            "count": 2,
            "value": [
                {
                    "id": 12346,
                    "status": "completed",
                    "result": "succeeded",
                    "sourceBranch": "refs/heads/main",
                    "startTime": "2024-01-02T10:00:00Z",
                    "definition": {"name": "Test Pipeline"},
                },
                {
                    "id": 12345,
                    "status": "completed",
                    "result": "failed",
                    "sourceBranch": "refs/heads/main",
                    "startTime": "2024-01-01T10:00:00Z",
                    "definition": {"name": "Test Pipeline"},
                },
            ],
        }

        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_cm.status = 200
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        response = self.adapter.list_recent_pipeline_runs(pipeline_id="123", top=2)

        self.assertIsInstance(response, ListRecentPipelineRunsResponse)
        self.assertEqual(response.pipeline_name, "Test Pipeline")
        self.assertEqual(len(response.runs), 2)
        self.assertEqual(response.runs[0].run_id, "12346")
        self.assertEqual(response.runs[1].result, PipelineResult.FAILED)

    @patch("building_blocks.mcp.devops_status_adapter.src.adapter.urlopen")
    def test_malformed_provider_payload_fails_closed(self, mock_urlopen):
        # Missing required 'status' field
        mock_response_data = {"id": 12345, "definition": {"name": "Test Pipeline"}}

        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_cm.status = 200
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        with self.assertRaisesRegex(RuntimeError, "Malformed provider response."):
            self.adapter.get_pipeline_run_status(pipeline_id="123", run_id="12345")

    @patch("building_blocks.mcp.devops_status_adapter.src.adapter.urlopen")
    def test_api_error_fails_closed(self, mock_urlopen):
        mock_cm = MagicMock()
        mock_cm.status = 404
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        with self.assertRaisesRegex(
            RuntimeError, "Internal error fetching DevOps status."
        ):
            self.adapter.get_pipeline_run_status(
                pipeline_id="123", run_id="nonexistent"
            )

    def test_credential_safety_in_headers(self):
        headers = self.adapter._get_headers()
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Basic "))
        # Ensure token is not present in plain text
        self.assertNotIn("test-token", headers["Authorization"])

    @patch("building_blocks.mcp.devops_status_adapter.src.adapter.urlopen")
    def test_list_recent_pipeline_runs_pagination_and_branch(self, mock_urlopen):
        # Verify top and branch parameters are passed correctly in URL
        mock_cm = MagicMock()
        mock_cm.read.return_value = json.dumps({"count": 0, "value": []}).encode(
            "utf-8"
        )
        mock_cm.status = 200
        mock_cm.__enter__.return_value = mock_cm
        mock_urlopen.return_value = mock_cm

        self.adapter.list_recent_pipeline_runs(
            pipeline_id="123", branch="refs/heads/feat", top=10
        )

        args, kwargs = mock_urlopen.call_args
        request = args[0]
        self.assertIn("%24top=10", request.full_url)
        self.assertIn("branchName=refs%2Fheads%2Ffeat", request.full_url)

    def test_rejected_unsafe_identifiers_via_contract(self):
        # The adapter uses contract models for validation on output.
        # While input validation usually happens at the tool entry point,
        # we can verify that the contract's SafeId pattern works as expected.
        from pydantic import TypeAdapter
        from building_blocks.mcp.devops_mcp_tool_contract.src.models import SafeId

        ta = TypeAdapter(SafeId)

        # Valid identifiers
        ta.validate_python("valid-id")
        ta.validate_python("valid.id")
        ta.validate_python("valid_id")
        ta.validate_python("valid id")

        # Invalid identifiers (rejected)
        with self.assertRaises(ValidationError):
            ta.validate_python("invalid/id")
        with self.assertRaises(ValidationError):
            ta.validate_python("invalid:id")
        with self.assertRaises(ValidationError):
            ta.validate_python("")


if __name__ == "__main__":
    unittest.main()
