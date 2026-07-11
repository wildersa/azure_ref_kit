import pytest
from unittest.mock import patch
from src.tool_implementation import (
    get_system_status,
    validate_tool_arguments,
    validate_tool_output,
)


def test_get_system_status_valid():
    """Verify get_system_status returns valid data."""
    result = get_system_status()
    assert result["business_status"] == "operational"
    assert "service_health" in result
    assert isinstance(result["active_regions"], list)


def test_validate_tool_arguments_valid():
    """Verify no arguments passes."""
    validate_tool_arguments({})


def test_validate_tool_arguments_invalid():
    """Verify unexpected arguments are rejected."""
    with pytest.raises(ValueError, match="does not accept parameters"):
        validate_tool_arguments({"unexpected": "param"})


def test_validate_tool_output_invalid():
    """Verify tool output validation fails for invalid data."""
    invalid_data = {"business_status": "broken"}  # Missing required fields
    with pytest.raises(RuntimeError, match="invalid response format"):
        validate_tool_output(invalid_data)


@patch("src.tool_implementation.SCHEMA_PATH")
def test_validate_tool_output_schema_missing(mock_path):
    """Verify error when schema file is missing."""
    mock_path.exists.return_value = False
    with pytest.raises(RuntimeError, match="invalid response format"):
        validate_tool_output({"some": "data"})
