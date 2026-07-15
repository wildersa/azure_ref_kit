import logging
import requests
from typing import Any, Dict, Optional
from .config import Settings
from .models import SubmitResponse, TaskStatusResponse

logger = logging.getLogger(__name__)


def submit_task(
    operation_type: str,
    parameters: Optional[Dict[str, Any]] = None,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    """
    Submits a task to the asynchronous queue function.
    Validates the response against a strict schema to prevent provider leakage.
    """
    if settings is None:
        settings = Settings()

    payload = {"operation_type": operation_type, "parameters": parameters or {}}

    try:
        # In a real environment, we would use managed identity to get a token if the function is protected.
        response = requests.post(settings.function_submit_url, json=payload, timeout=10)

        if response.status_code == 202:
            try:
                raw_data = response.json()
                # P0: Explicitly construct the allowed response shape and reject extra fields
                validated = SubmitResponse(**raw_data)
                return validated.model_dump(mode="json")
            except Exception:
                logger.error("Failed to parse or validate submission response.")
                return {"error": "The service returned an invalid response."}

        logger.error("Failed to submit task. Service returned non-success status.")
        return {"error": "The task submission service is currently unavailable."}
    except Exception:
        # P0: Avoid logging exception text or internal details
        logger.error("Error calling submit function.")
        return {"error": "An error occurred while submitting the task."}


def get_task_status(
    correlation_id: str, settings: Optional[Settings] = None
) -> Dict[str, Any]:
    """
    Retrieves the status of a task from the status boundary.
    Validates the response against a strict schema to prevent provider leakage.
    """
    if settings is None:
        settings = Settings()

    # P0: Basic validation of correlation_id format before making the call
    if (
        not correlation_id
        or not isinstance(correlation_id, str)
        or len(correlation_id) < 8
        or len(correlation_id) > 64
    ):
        return {"error": "Invalid correlation ID provided."}

    url = settings.function_status_url_template.format(correlation_id=correlation_id)

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            try:
                raw_data = response.json()
                # P0: Explicitly construct the allowed response shape and reject extra fields
                validated = TaskStatusResponse(**raw_data)
                return validated.model_dump(mode="json")
            except Exception:
                logger.error("Failed to parse or validate status response.")
                return {"error": "The service returned an invalid response."}
        elif response.status_code == 404:
            return {"error": "Task not found. Please verify the correlation ID."}

        logger.error("Failed to get task status. Service returned non-success status.")
        return {"error": "The status service is currently unavailable."}
    except Exception:
        # P0: Avoid logging exception text or internal details
        logger.error("Error calling status function.")
        return {"error": "An error occurred while retrieving the task status."}
