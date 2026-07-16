import json
from pathlib import Path
import pytest

MODULE_DIR = Path(__file__).parent.parent
API_FILE = MODULE_DIR / "src" / "api.ts"

def test_payload_bounds_defined_in_api():
    """Ensure that MAX_STR_LEN and other bounds are defined in the API adapter."""
    with open(API_FILE, "r") as f:
        content = f.read()

    assert "MAX_STR_LEN = 64" in content
    assert "MAX_LONG_STR_LEN = 1000" in content
    assert "MAX_ARTIFACTS = 50" in content
    assert "data.steps.length > 50" in content

def test_schema_alignment_with_api():
    """Verify that API adapter logic aligns with shared contract expectations."""
    # This is a static analysis check of the TypeScript code for contract alignment
    with open(API_FILE, "r") as f:
        content = f.read()

    # Check for strict validation calls
    assert "validateAndSanitizeStatus" in content
    assert "validateAndSanitizeStep" in content
    assert "validateAndSanitizeFailure" in content

    # Check for fail-closed behavior (throwing ValidationError)
    assert "throw new ValidationError" in content
