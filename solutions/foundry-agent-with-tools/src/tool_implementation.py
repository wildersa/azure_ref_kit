import json
import logging
from pathlib import Path
from typing import Any, Dict
import jsonschema

logger = logging.getLogger(__name__)

# Path to the contract schema for validation
SCHEMA_PATH = Path(__file__).parent.parent / "contracts" / "system-status.schema.json"


def get_system_status() -> Dict[str, Any]:
    """
    Executes the system status tool logic with deterministic mock data.
    Validates the output against the system-status schema before returning.
    """
    # Deterministic mock data for local execution/tests
    # In a real scenario, this might call an internal API or Azure resource
    status_data = {
        "business_status": "operational",
        "service_health": "Healthy",
        "active_regions": ["eastus", "westus2"],
        "last_updated": "2026-07-03T10:00:00Z",
        "environment": "production",
    }

    validate_tool_output(status_data)
    return status_data


def validate_tool_output(data: Dict[str, Any]) -> None:
    """Validates the tool output against the defined contract."""
    try:
        if not SCHEMA_PATH.exists():
            raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

        with open(SCHEMA_PATH, "r") as f:
            schema = json.load(f)

        jsonschema.validate(instance=data, schema=schema)
    except (jsonschema.ValidationError, json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Tool contract validation failed: {e}")
        # Redact internal technical details in the error returned to the agent
        raise RuntimeError("The status tool returned an invalid response format.")


def validate_tool_arguments(arguments: Dict[str, Any]) -> None:
    """
    Validates tool arguments.
    For get_system_status, no arguments are expected.
    """
    if arguments:
        logger.warning(f"Unexpected arguments received for system-status: {arguments}")
        # Reject if any arguments are provided, as the contract defines an empty properties object
        raise ValueError(
            "Invalid tool arguments: get_system_status does not accept parameters."
        )
