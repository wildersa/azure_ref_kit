import logging
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urlparse
from .models import DevOpsStatusRequest, DevOpsStatusResponse, BuildStatus, BuildResult
from .client import DevOpsClient
from .config import validate_organization_url, validate_project_identifier, Settings

logger = logging.getLogger(__name__)


def validate_portal_url(portal_url: str, organization_url: str) -> None:
    """
    Validates that the portal URL returned by the provider is safe.
    Must be HTTPS and match the host and organization of the requested organization.
    """
    portal_parsed = urlparse(portal_url)
    org_parsed = urlparse(organization_url)

    if portal_parsed.scheme != "https":
        raise ValueError("Provider returned an unsafe non-HTTPS portal URL.")

    # Azure DevOps portal URLs usually match the org host or dev.azure.com
    # Both host and path segments are checked for cross-tenant spoofing.

    # 1. Host validation
    # Standard hosts allowed: dev.azure.com and visualstudio.com
    # We allow the specific requested host and dev.azure.com as a fallthrough.
    allowed_hosts = {org_parsed.netloc, "dev.azure.com"}
    if portal_parsed.netloc not in allowed_hosts and not portal_parsed.netloc.endswith(
        ".visualstudio.com"
    ):
        raise ValueError("Provider returned a portal URL with an untrusted host.")

    # 2. Cross-tenant check: ensure the organization name matches
    # For dev.azure.com/{org}, the first path segment is the org name
    # For {org}.visualstudio.com, the netloc contains the org name
    def get_org_name(parsed_url: Any) -> str:
        if parsed_url.netloc == "dev.azure.com":
            # path is usually /org/project/...
            parts = [p for p in parsed_url.path.split("/") if p]
            return parts[0] if parts else ""
        elif ".visualstudio.com" in parsed_url.netloc:
            # host is org.visualstudio.com
            return parsed_url.netloc.split(".")[0]
        else:
            # Unexpected format, return netloc for comparison if no better option
            return parsed_url.netloc

    requested_org = get_org_name(org_parsed)
    returned_org = get_org_name(portal_parsed)

    if not requested_org or requested_org.lower() != returned_org.lower():
        # This prevents a malicious or misconfigured response from redirecting
        # an agent to a different organization on the same host.
        raise ValueError("Provider returned a portal URL for a different organization.")


def get_build_status(
    request_params: Dict[str, Any], client: DevOpsClient
) -> DevOpsStatusResponse:
    """
    Core tool logic: validates input, fetches build from Azure DevOps,
    and maps it to a customer-safe status response.
    """
    try:
        # 1. Validate request parameters
        try:
            request = DevOpsStatusRequest(**request_params)
        except Exception:
            # Customer-Safe Logging: Do not log the raw exception/parameters
            logger.warning("Invalid request parameters received.")
            raise ValueError("Invalid request parameters.")

        validate_organization_url(request.organization_url)
        validate_project_identifier(request.project)

        # 2. Fetch build from Azure DevOps
        raw_build = client.get_build(
            str(request.organization_url), request.project, request.build_id
        )

        # 3. Map to safe response model
        # Documentation: https://learn.microsoft.com/en-us/rest/api/azure/devops/build/builds/get?view=azure-devops-rest-7.1#build

        # Safely extract values from the provider payload
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
            try:
                # Standard Python datetime can handle Z since 3.11, or replace Z with +00:00
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                return None

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

        # Safety Check: Validate the portal URL host and organization
        validate_portal_url(portal_url, str(request.organization_url))

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

    except ValueError:
        # Customer-Safe Logging: Log a fixed message without technical detail
        logger.warning("Build status request failed due to validation or missing data.")
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
