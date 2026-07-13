import json
import os
from typing import Any, Dict
import jsonschema

# Load schemas once at module level
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")

with open(os.path.join(SCHEMA_DIR, "customer_safe_status.schema.json"), "r") as f:
    STATUS_SCHEMA = json.load(f)

with open(os.path.join(SCHEMA_DIR, "friendly_failure.schema.json"), "r") as f:
    FAILURE_SCHEMA = json.load(f)


def validate_status(data: Dict[str, Any]) -> None:
    """Validates the input dictionary against the CustomerSafeStatus schema.

    Args:
        data: The dictionary to validate.

    Raises:
        jsonschema.ValidationError: If the data does not conform to the schema.
    """
    jsonschema.validate(instance=data, schema=STATUS_SCHEMA)


def validate_failure(data: Dict[str, Any]) -> None:
    """Validates the input dictionary against the FriendlyFailure schema.

    Args:
        data: The dictionary to validate.

    Raises:
        jsonschema.ValidationError: If the data does not conform to the schema.
    """
    jsonschema.validate(instance=data, schema=FAILURE_SCHEMA)


def sanitize_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministically strips unknown or forbidden fields from a status dictionary.
    Only fields explicitly allowed by the schema are preserved.

    Args:
        data: The input dictionary to sanitize.

    Returns:
        A new dictionary containing only the fields allowed by the CustomerSafeStatus schema.
    """
    allowed_keys = STATUS_SCHEMA.get("properties", {}).keys()
    sanitized = {k: v for k, v in data.items() if k in allowed_keys}
    # For nested objects like safe_artifacts, we could recurse if needed,
    # but the schema for safe_artifacts already has additionalProperties: false.
    # To be safe, we rebuild the list of artifacts too.
    if "safe_artifacts" in sanitized and isinstance(sanitized["safe_artifacts"], list):
        artifact_keys = STATUS_SCHEMA["properties"]["safe_artifacts"]["items"][
            "properties"
        ].keys()
        sanitized["safe_artifacts"] = [
            {k: v for k, v in art.items() if k in artifact_keys}
            for art in sanitized["safe_artifacts"]
            if isinstance(art, dict)
        ]
    return sanitized


def sanitize_failure(data: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministically strips unknown or forbidden fields from a failure dictionary.
    Only fields explicitly allowed by the schema are preserved.

    Args:
        data: The input dictionary to sanitize.

    Returns:
        A new dictionary containing only the fields allowed by the FriendlyFailure schema.
    """
    allowed_keys = FAILURE_SCHEMA.get("properties", {}).keys()
    sanitized = {k: v for k, v in data.items() if k in allowed_keys}
    return sanitized
