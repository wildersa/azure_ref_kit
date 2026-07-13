import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode

from pydantic import ValidationError

# We assume the contract is available in the python path
try:
    from building_blocks.mcp.devops_mcp_tool_contract.src.models import (
        GetPipelineRunStatusResponse,
        PipelineStatus,
        PipelineResult,
        ListRecentPipelineRunsResponse,
        PipelineRunSummary,
    )
except ImportError:
    # Fallback for local testing if needed, though CI/standard run should have it in PYTHONPATH
    import sys
    import os

    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    )
    from building_blocks.mcp.devops_mcp_tool_contract.src.models import (
        GetPipelineRunStatusResponse,
        PipelineStatus,
        PipelineResult,
        ListRecentPipelineRunsResponse,
        PipelineRunSummary,
    )

logger = logging.getLogger(__name__)


class DevOpsStatusAdapter:
    """Controlled read-only adapter for Azure DevOps status queries."""

    def __init__(
        self,
        organization_url: str,
        project: str,
        token: str,
        api_version: str = "7.1",
    ):
        """
        Initialize the adapter.

        Args:
            organization_url: The Azure DevOps organization URL (e.g., https://dev.azure.com/org).
            project: The project name or ID.
            token: The Personal Access Token (PAT).
            api_version: The Azure DevOps REST API version.
        """
        self.organization_url = organization_url.rstrip("/")
        self.project = quote(project)
        self.token = token
        self.api_version = api_version

    def _get_headers(self) -> Dict[str, str]:
        """Construct headers for the REST API request."""
        import base64

        auth = base64.b64encode(f":{self.token}".encode("ascii")).decode("ascii")
        return {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": f"application/json;api-version={self.api_version}",
        }

    def _make_request(self, url: str) -> Dict[str, Any]:
        """Perform a GET request to the Azure DevOps API."""
        request = Request(url, headers=self._get_headers(), method="GET")
        try:
            with urlopen(request) as response:
                if response.status != 200:
                    logger.error(f"Azure DevOps API returned status {response.status}")
                    raise RuntimeError(f"Azure DevOps API error: {response.status}")
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            logger.error(f"Failed to fetch from Azure DevOps: {str(e)}")
            # Fail closed: do not expose internal error details to the response
            raise RuntimeError("Internal error fetching DevOps status.")

    def get_pipeline_run_status(
        self, pipeline_id: str, run_id: str
    ) -> GetPipelineRunStatusResponse:
        """
        Get the status of a specific pipeline run (Build).

        Maps to: GET https://dev.azure.com/{organization}/{project}/_apis/build/builds/{buildId}
        """
        # Validate inputs using contract's SafeId constraint implicitly or explicitly
        # Here we just use them in the URL construction safely
        safe_run_id = quote(run_id)
        url = f"{self.organization_url}/{self.project}/_apis/build/builds/{safe_run_id}"

        raw_data = self._make_request(url)

        # Map raw data to contract model
        try:
            # Azure DevOps Build properties:
            # status: 'all', 'cancelling', 'completed', 'inProgress', 'none', 'notStarted', 'postponed'
            # result: 'canceled', 'failed', 'none', 'partiallySucceeded', 'succeeded'

            # Note: pipeline_id in request might be different from what's in the response definition id
            # We use the response data for mapping.

            # Start and finish times are ISO 8601 strings in ADO
            start_time = datetime.fromisoformat(
                raw_data["startTime"].replace("Z", "+00:00")
            )
            end_time = None
            if raw_data.get("finishTime"):
                end_time = datetime.fromisoformat(
                    raw_data["finishTime"].replace("Z", "+00:00")
                )

            duration = None
            if start_time and end_time:
                duration = int((end_time - start_time).total_seconds())

            return GetPipelineRunStatusResponse(
                pipeline_name=raw_data["definition"]["name"],
                run_id=str(raw_data["id"]),
                status=PipelineStatus(raw_data["status"]),
                result=PipelineResult(raw_data.get("result", "none")),
                branch=raw_data["sourceBranch"],
                commit_sha=raw_data.get("sourceVersion")[:7]
                if raw_data.get("sourceVersion")
                else None,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
                summary=f"Build {raw_data['buildNumber']} {raw_data.get('result', raw_data['status'])}.",
                portal_url=raw_data["_links"]["web"]["href"],
            )
        except (KeyError, ValueError, ValidationError) as e:
            logger.error(f"Failed to map Azure DevOps response: {str(e)}")
            raise RuntimeError("Malformed provider response.")

    def list_recent_pipeline_runs(
        self, pipeline_id: str, branch: Optional[str] = None, top: int = 5
    ) -> ListRecentPipelineRunsResponse:
        """
        List recent runs for a pipeline.

        Maps to: GET https://dev.azure.com/{organization}/{project}/_apis/build/builds?definitions={pipeline_id}&branchName={branch}&$top={top}
        """
        params = {
            "definitions": pipeline_id,
            "$top": top,
        }
        if branch:
            params["branchName"] = branch

        query_string = urlencode(params)
        url = (
            f"{self.organization_url}/{self.project}/_apis/build/builds?{query_string}"
        )

        raw_data = self._make_request(url)

        try:
            runs = []
            pipeline_name = "Unknown"
            if raw_data["count"] > 0:
                pipeline_name = raw_data["value"][0]["definition"]["name"]
                for build in raw_data["value"]:
                    runs.append(
                        PipelineRunSummary(
                            run_id=str(build["id"]),
                            status=PipelineStatus(build["status"]),
                            result=PipelineResult(build.get("result", "none")),
                            branch=build["sourceBranch"],
                            start_time=datetime.fromisoformat(
                                build["startTime"].replace("Z", "+00:00")
                            ),
                        )
                    )

            return ListRecentPipelineRunsResponse(
                pipeline_name=pipeline_name, runs=runs
            )
        except (KeyError, ValueError, ValidationError) as e:
            logger.error(f"Failed to map Azure DevOps response: {str(e)}")
            raise RuntimeError("Malformed provider response.")
