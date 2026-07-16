import json
import math
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import jsonschema

# Path to the shared contract schema
SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "../../../../shared/contracts/cost-ledger.schema.json"
)

# Constants for boundaries
MAX_STRING_LENGTH = 128
FORBIDDEN_PATTERNS = [
    # GUIDs (Subscription IDs, Tenant IDs)
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    # Azure Resource IDs
    r"/subscriptions/|/resourceGroups/|/providers/",
    # Secrets and tokens
    r"AccountKey=",
    r"sig=",
    r"Bearer\s+",
    r"client_secret",
]


def _load_schema() -> Dict[str, Any]:
    """Loads the cost ledger schema from the shared contracts directory."""
    with open(SCHEMA_PATH, "r") as f:
        return json.load(f)


def _validate_boundaries(data: Dict[str, Any]) -> None:
    """Performs additional boundary and security checks not covered by the JSON schema."""
    for key, value in data.items():
        # 1. String length limits
        if isinstance(value, str):
            if len(value) > MAX_STRING_LENGTH:
                raise ValueError(
                    f"Field '{key}' exceeds maximum length of {MAX_STRING_LENGTH}"
                )

            # 2. Forbidden patterns (Subscription IDs, secrets, etc.)
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    raise ValueError(
                        f"Field '{key}' contains forbidden technical or billing information."
                    )

        # 3. Non-negative finite amounts
        if isinstance(value, (int, float)):
            if value < 0:
                raise ValueError(f"Field '{key}' must be non-negative.")
            if not math.isfinite(value):
                raise ValueError(f"Field '{key}' must be a finite number.")


def capture_cost_entry(
    run_id: str,
    category: str,
    estimated_amount: float,
    step_name: Optional[str] = None,
    provider: Optional[str] = None,
    model_or_service: Optional[str] = None,
    input_units: Optional[float] = None,
    output_units: Optional[float] = None,
    unit_name: Optional[str] = None,
    currency: str = "USD",
    created_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates and validates a bounded estimated cost ledger entry.

    Args:
        run_id: Unique identifier for the pipeline run.
        category: Cost category (e.g., ai_tokens, storage).
        estimated_amount: The estimated cost amount.
        step_name: Name of the pipeline step.
        provider: Service provider (e.g., Azure).
        model_or_service: Specific model or service used.
        input_units: Number of input units.
        output_units: Number of output units.
        unit_name: Name of the unit (e.g., token).
        currency: Currency code (default: USD).
        created_at: ISO-8601 timestamp. If None, current UTC time is used.

    Returns:
        A validated dictionary conforming to the cost-ledger.schema.json contract.

    Raises:
        jsonschema.ValidationError: If the entry does not conform to the schema.
        ValueError: If boundary or security checks fail.
    """
    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()

    entry = {
        "run_id": run_id,
        "category": category,
        "estimated_amount": estimated_amount,
        "step_name": step_name,
        "provider": provider,
        "model_or_service": model_or_service,
        "input_units": input_units,
        "output_units": output_units,
        "unit_name": unit_name,
        "currency": currency,
        "created_at": created_at,
    }

    # Remove None values so they don't trigger schema errors if null is not allowed
    # (Though the schema says ["string", "null"] for many fields)
    entry = {k: v for k, v in entry.items() if v is not None}

    # 1. Validate additional boundaries and security
    _validate_boundaries(entry)

    # 2. Validate against the shared JSON schema
    schema = _load_schema()
    jsonschema.validate(instance=entry, schema=schema)

    return entry
