import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable
from urllib.request import Request, urlopen
from urllib.parse import quote, urlencode, urlparse

from pydantic import ValidationError, TypeAdapter

# We assume the contract is available in the python path
try:
    from building_blocks.mcp.devops_mcp_tool_contract.src.models import (
        GetPipelineRunStatusResponse,
        PipelineStatus,
        PipelineResult,
        ListRecentPipelineRunsResponse,
        PipelineRunSummary,
        SafeId,
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
        SafeId,
    )

logger = logging.getLogger(__name__)


def default_transport(request: Request) -> Any:
    """Default HTTP transport using urllib.request.urlopen."""
    with urlopen(request) as response:
        return response.read(), response.status


class DevOpsStatusAdapter:
    """Controlled read-only adapter for Azure DevOps status queries."""

    ALLOWED_HOSTS = ["dev.azure.com"]
    _safe_id_adapter = TypeAdapter(SafeId)

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
            token: The Personal Access Token (PAT) or Entra ID Bearer token.
            api_version: The Azure DevOps REST API version.
            transport: Optional injectable HTTP transport for testing and isolation.
        """
        self._validate_url(organization_url)
        # Validate project name at init
        self._safe_id_adapter.validate_python(project)

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
        # Detect if the token is likely an Entra ID Bearer token or a PAT
        # PATs are usually shorter and don't look like JWTs.
        # Entra tokens for Azure DevOps are Bearer tokens.
        if self.token.startswith("ey") and len(self.token) > 100:
            auth_header = f"Bearer {self.token}"
        else:
            import base64

            auth = base64.b64encode(f":{self.token}".encode("ascii")).decode("ascii")
            auth_header = f"Basic {auth}"

        return {
            "Authorization": auth_header,
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
        # Validate identifiers at the boundary
        self._safe_id_adapter.validate_python(pipeline_id)
        self._safe_id_adapter.validate_python(run_id)

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
        # Validate identifiers and bounds at the boundary
        self._safe_id_adapter.validate_python(pipeline_id)
        if branch:
            self._safe_id_adapter.validate_python(branch)

        # Enforce top bounds (1-20 as per contract ListRecentPipelineRunsRequest)
        if not (1 <= top <= 20):
            raise ValueError("top must be between 1 and 20")

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
