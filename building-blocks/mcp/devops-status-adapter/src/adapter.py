import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode, urlparse

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


def default_transport(request: Request) -> Any:
    """Default HTTP transport using urllib.request.urlopen."""
    with urlopen(request) as response:
        return response.read(), response.status


class DevOpsStatusAdapter:
    """Controlled read-only adapter for Azure DevOps status queries."""

    ALLOWED_HOSTS = ["dev.azure.com"]

    def __init__(
        self,
        organization_url: str,
        project: str,
        token: str,
        api_version: str = "7.1",
        transport: Optional[Callable[[Request], Any]] = None,
    ):
        """
        Initialize the adapter.

        Args:
            organization_url: The Azure DevOps organization URL (e.g., https://dev.azure.com/org).
            project: The project name or ID.
            token: The Personal Access Token (PAT).
            api_version: The Azure DevOps REST API version.
            transport: Optional injectable HTTP transport for testing and isolation.
        """
        self._validate_url(organization_url)
        self.organization_url = organization_url.rstrip("/")
        self.project = quote(project)
        self.token = token
        self.api_version = api_version
        self.transport = transport or default_transport

    def _validate_url(self, url: str) -> None:
        """Ensure the URL targets a trusted Azure DevOps host."""
        parsed = urlparse(url)
        if parsed.netloc not in self.ALLOWED_HOSTS:
            logger.error("Attempted access to unauthorized host.")
            raise ValueError("Invalid organization_url: only dev.azure.com is allowed.")

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
        """Perform a GET request using the injected transport."""
        request = Request(url, headers=self._get_headers(), method="GET")
        try:
            body, status = self.transport(request)
            if status != 200:
                logger.error(f"Provider returned error status: {status}")
                raise RuntimeError("Provider error.")
            return json.loads(body.decode("utf-8"))
        except Exception:
            # Sanitize logging: do not log the raw exception string/technical details
            logger.error("Failed to fetch from provider due to technical error.")
            # Fail closed: do not expose internal error details to the response
            raise RuntimeError("Internal error fetching DevOps status.")

    def get_pipeline_run_status(
        self, pipeline_id: str, run_id: str
    ) -> GetPipelineRunStatusResponse:
        """
        Get the status of a specific pipeline run (Build).

        Maps to: GET https://dev.azure.com/{organization}/{project}/_apis/build/builds/{buildId}
        """
        safe_run_id = quote(run_id)
        url = f"{self.organization_url}/{self.project}/_apis/build/builds/{safe_run_id}"

        raw_data = self._make_request(url)

        try:
            # Map raw data to contract model
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
        except (KeyError, ValueError, ValidationError):
            logger.error("Failed to map provider response due to schema mismatch.")
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
        except (KeyError, ValueError, ValidationError):
            logger.error("Failed to map provider list response due to schema mismatch.")
            raise RuntimeError("Malformed provider response.")
