import base64
import json
import logging
import urllib.request
import urllib.error
import urllib.parse
from typing import Any, Dict


logger = logging.getLogger(__name__)


class DevOpsClient:
    """
    Minimal, injectable client boundary for the Azure DevOps REST API.
    Uses urllib.request for a dependency-free implementation.
    """

    def __init__(self, pat: str, timeout: int = 30):
        self._pat = pat
        self._timeout = timeout

    def get_build(
        self, organization_url: str, project: str, build_id: int
    ) -> Dict[str, Any]:
        """
        Retrieves exactly one build by project and build ID.
        API: GET https://dev.azure.com/{organization}/{project}/_apis/build/builds/{buildId}?api-version=7.1
        """
        # Ensure trailing slash on organization_url for clean concatenation if needed,
        # but the standard format is without it.
        base_url = organization_url.rstrip("/")
        # URL encode the project identifier to support spaces and special characters
        encoded_project = urllib.parse.quote(project)
        url = f"{base_url}/{encoded_project}/_apis/build/builds/{build_id}?api-version=7.1"

        # Basic Auth header: base64(user:pass). For PAT, user is empty.
        auth_str = f":{self._pat}"
        encoded_auth = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Accept": "application/json",
            "User-Agent": "AzureReferenceKit-DevOpsStatusTool/1.0",
        }

        request = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
                else:
                    # This branch might not be hit for some status codes as urlopen raises HTTPError
                    logger.error("Unexpected response status from Azure DevOps.")
                    raise RuntimeError("Failed to retrieve build status.")

        except urllib.error.HTTPError as e:
            if e.code == 404:
                logger.warning("Build or project not found.")
                raise ValueError("Build not found.")
            elif e.code == 401:
                logger.error("Authentication failed. Check AZURE_DEVOPS_PAT.")
                raise PermissionError("Authentication failed.")
            else:
                logger.error("Azure DevOps API HTTP error.")
                raise RuntimeError("Azure DevOps API error.")

        except urllib.error.URLError:
            # Customer-Safe Logging: Redact internal technical details (e.g. e.reason which may contain IPs)
            logger.error("Failed to connect to Azure DevOps.")
            raise ConnectionError("Failed to connect to Azure DevOps.")

        except Exception:
            # Customer-Safe Logging: Redact internal technical details
            logger.error("An unexpected error occurred during API call.")
            raise RuntimeError("An unexpected error occurred.")
