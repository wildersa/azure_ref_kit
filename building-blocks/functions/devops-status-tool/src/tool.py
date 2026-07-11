import logging
from datetime import datetime
from typing import Any, Dict, Optional
from .models import DevOpsStatusRequest, DevOpsStatusResponse, BuildStatus, BuildResult
from .client import DevOpsClient
from .config import validate_organization_url, validate_project_identifier, Settings

logger = logging.getLogger(__name__)


def get_build_status(
    request_params: Dict[str, Any], client: DevOpsClient
) -> DevOpsStatusResponse:
    """
    Core tool logic: validates input, fetches build from Azure DevOps,
    and maps it to a customer-safe status response.
    """
    try:
        # 1. Validate request parameters
        request = DevOpsStatusRequest(**request_params)
        validate_organization_url(request.organization_url)
        validate_project_identifier(request.project)

        # 2. Fetch build from Azure DevOps
        raw_build = client.get_build(
            str(request.organization_url), request.project, request.build_id
        )

        # 3. Map to safe response model
        # Documentation: https://learn.microsoft.com/en-us/rest/api/azure/devops/build/builds/get?view=azure-devops-rest-7.1#build

        # Safely extract values from the provider payload
        # status and result are enums in the API and our model
        status = raw_build.get("status", "none")
        result = raw_build.get("result", "none")

        # Parse timestamps
        queue_time_str = raw_build.get("queueTime")
        start_time_str = raw_build.get("startTime")
        finish_time_str = raw_build.get("finishTime")

        # Helper to parse ISO8601 from Azure DevOps (usually ends with Z)
        def parse_timestamp(ts: Optional[str]) -> Optional[datetime]:
            if not ts:
                return None
            # Standard Python datetime can handle Z since 3.11, or replace Z with +00:00
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))

        queue_time = parse_timestamp(queue_time_str)
        start_time = parse_timestamp(start_time_str)
        end_time = parse_timestamp(finish_time_str)

        # Calculate duration if possible
        duration_seconds = None
        if start_time and end_time:
            duration_seconds = int((end_time - start_time).total_seconds())

        # Sanitized portal URL from _links.web.href
        portal_url = raw_build.get("_links", {}).get("web", {}).get("href")
        if not portal_url:
            raise ValueError("Build portal URL is missing in provider response.")

        # Friendly business-level summary
        pipeline_name = raw_build.get("definition", {}).get("name", "Unknown Pipeline")
        summary = f"Pipeline '{pipeline_name}' build {request.build_id} is {status}"
        if result and result != "none":
            summary += f" with result: {result}"

        response = DevOpsStatusResponse(
            pipeline_name=pipeline_name,
            run_id=str(raw_build.get("id", request.build_id)),
            status=BuildStatus(status),
            result=BuildResult(result),
            branch="redacted",  # P0: Never expose branch names
            queue_time=queue_time,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,
            summary=summary,
            portal_url=portal_url,
        )

        return response

    except ValueError as e:
        logger.warning(f"Validation error or missing data: {str(e)}")
        raise
    except Exception:
        # Customer-Safe Logging: Redact internal technical details
        logger.error("Error in get_build_status mapping.")
        raise RuntimeError("Failed to retrieve or map build status.")


def get_build_status_safe(request_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Module entrypoint for agent tool callers.
    Handles internal dependency initialization (PAT from env).
    Returns a raw dict for compatibility with agent runtime.
    """
    settings = Settings.from_env()
    client = DevOpsClient(pat=settings.devops_pat)
    response = get_build_status(request_params, client)
    return response.model_dump(mode="json")
