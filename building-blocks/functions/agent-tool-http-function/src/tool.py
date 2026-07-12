import logging
from typing import Any, Dict
from .models import ResourceInfoRequest, ResourceInfoResponse, ResourceStatus

logger = logging.getLogger(__name__)


def get_resource_info(request_params: Dict[str, Any]) -> ResourceInfoResponse:
    """
    Core tool logic: validates input and returns deterministic mock data.
    In a real scenario, this would call an Azure API.
    """
    try:
        # 1. Validate request parameters
        try:
            request = ResourceInfoRequest(**request_params)
        except Exception:
            logger.warning("Invalid request parameters received.")
            raise ValueError("Invalid request parameters.")

        # 2. Mock logic for deterministic behavior
        # In this reference implementation, we return mocked data based on the resource_id.

        # Determine status based on the last character of resource_id (for determinism)
        last_char = request.resource_id[-1].lower()
        if last_char in "abcde":
            status = ResourceStatus.RUNNING
        elif last_char in "fghij":
            status = ResourceStatus.STOPPED
        elif last_char in "klmno":
            status = ResourceStatus.DEGRADED
        else:
            status = ResourceStatus.UNKNOWN

        # Determine location based on the first character
        first_char = request.resource_id[0].lower()
        if first_char in "abcdef":
            location = "eastus"
        elif first_char in "ghijkl":
            location = "westus"
        else:
            location = "northeurope"

        summary = f"Resource '{request.resource_id}' ({request.resource_type.value}) is currently {status.value} in {location}."

        response = ResourceInfoResponse(
            resource_id=request.resource_id,
            resource_type=request.resource_type,
            status=status,
            location=location,
            tags={"environment": "production", "owner": "platform-team"},
            summary=summary,
        )

        return response

    except ValueError:
        logger.warning("Resource info request failed due to validation.")
        raise
    except Exception as e:
        # Customer-Safe Logging: Redact internal technical details
        logger.error(f"Error in get_resource_info: {str(e)}")  # Internal log
        raise RuntimeError("Failed to retrieve resource information.")


def get_resource_info_safe(request_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Module entrypoint for agent tool callers.
    Returns a raw dict for compatibility with agent runtime.
    """
    response = get_resource_info(request_params)
    return response.model_dump(mode="json")
