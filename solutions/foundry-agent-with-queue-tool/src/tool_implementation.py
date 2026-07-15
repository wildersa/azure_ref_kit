import logging
import requests
from typing import Any, Dict, Optional
from .config import Settings

logger = logging.getLogger(__name__)


def submit_task(
    operation_type: str,
    parameters: Optional[Dict[str, Any]] = None,
    settings: Optional[Settings] = None,
) -> Dict[str, Any]:
    """
    Submits a task to the asynchronous queue function.
    """
    if settings is None:
        settings = Settings()

    payload = {"operation_type": operation_type, "parameters": parameters or {}}

    try:
        # In a real environment, we would use managed identity to get a token if the function is protected.
        # For this reference, we assume standard HTTP call to the boundary.
        response = requests.post(settings.function_submit_url, json=payload, timeout=10)

        if response.status_code == 202:
            return response.json()

        logger.error(f"Failed to submit task. Status: {response.status_code}")
        return {"error": "The task submission service is currently unavailable."}
    except Exception as e:
        logger.error(f"Error calling submit function: {str(e)}")
        return {"error": "An error occurred while submitting the task."}


def get_task_status(
    correlation_id: str, settings: Optional[Settings] = None
) -> Dict[str, Any]:
    """
    Retrieves the status of a task from the status boundary.
    """
    if settings is None:
        settings = Settings()

    # P0: Basic validation of correlation_id format before making the call
    if (
        not correlation_id
        or not isinstance(correlation_id, str)
        or len(correlation_id) < 8
    ):
        return {"error": "Invalid correlation ID provided."}

    url = settings.function_status_url_template.format(correlation_id=correlation_id)

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": "Task not found. Please verify the correlation ID."}

        logger.error(f"Failed to get task status. Status: {response.status_code}")
        return {"error": "The status service is currently unavailable."}
    except Exception as e:
        logger.error(f"Error calling status function: {str(e)}")
        return {"error": "An error occurred while retrieving the task status."}
