from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationFieldResult:
    name: str
    is_valid: bool
    error_message: Optional[str] = None


@dataclass
class ValidationReport:
    status: str  # "valid", "invalid", "warning"
    missing_fields: List[str] = field(default_factory=list)
    invalid_fields: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_status": self.status,
            "missing_fields": self.missing_fields,
            "invalid_fields": self.invalid_fields,
        }


def validate_fields(
    extracted_data: Dict[str, Any], ruleset: Dict[str, Any]
) -> ValidationReport:
    """
    Validates extracted fields against a ruleset.
    Deterministic and local to this worker.
    """
    missing_fields = []
    invalid_fields = []

    fields = extracted_data.get("fields", {})
    required_fields = ruleset.get("required_fields", [])
    confidence_threshold = ruleset.get("confidence_threshold", 0.0)
    field_types = ruleset.get("field_types", {})

    # 1. Check required fields
    for req_field in required_fields:
        if req_field not in fields:
            missing_fields.append(req_field)

    # 2. Check types and confidence
    for field_name, field_data in fields.items():
        val = field_data.get("value")
        conf = field_data.get("confidence", 1.0)

        # Confidence check
        if conf < confidence_threshold:
            invalid_fields.append(
                {
                    "field": field_name,
                    "reason": f"Confidence {conf} is below threshold {confidence_threshold}",
                }
            )
            continue

        # Type check
        expected_type = field_types.get(field_name)
        if expected_type:
            if not _check_type(val, expected_type):
                invalid_fields.append(
                    {
                        "field": field_name,
                        "reason": f"Value '{val}' does not match expected type {expected_type}",
                    }
                )

    # Determine status
    if missing_fields or any(
        f for f in invalid_fields if "Confidence" not in f["reason"]
    ):
        status = "invalid"
    elif invalid_fields:
        status = "warning"
    else:
        status = "valid"

    return ValidationReport(
        status=status, missing_fields=missing_fields, invalid_fields=invalid_fields
    )


def _check_type(value: Any, expected_type: str) -> bool:
    if value is None:
        return False

    if expected_type == "number":
        return isinstance(value, (int, float))
    elif expected_type == "string":
        return isinstance(value, str)
    elif expected_type == "date":
        # Simple string-based date check for this implementation
        # In a real scenario, use dateutil.parser
        return isinstance(value, str) and len(value) >= 8

    return True
