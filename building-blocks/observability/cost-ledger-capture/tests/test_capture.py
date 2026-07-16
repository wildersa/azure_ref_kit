import pytest
import sys
import os
from jsonschema import ValidationError

# Correct path for local imports during tests
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from capture import capture_cost_entry


def test_capture_cost_entry_valid():
    """Test creating a valid cost ledger entry."""
    entry = capture_cost_entry(
        run_id="run-123",
        category="ai_tokens",
        estimated_amount=0.005,
        step_name="ocr_step",
        provider="Azure",
        model_or_service="gpt-4o",
        input_units=1000,
        output_units=500,
        unit_name="token",
    )
    assert entry["run_id"] == "run-123"
    assert entry["category"] == "ai_tokens"
    assert entry["estimated_amount"] == 0.005
    assert "created_at" in entry


def test_capture_cost_entry_invalid_category():
    """Test that an invalid category raises a ValidationError."""
    with pytest.raises(ValidationError):
        capture_cost_entry(
            run_id="run-123", category="invalid_category", estimated_amount=1.0
        )


def test_capture_cost_entry_negative_amount():
    """Test that a negative amount raises a ValueError."""
    with pytest.raises(ValueError, match="must be non-negative"):
        capture_cost_entry(
            run_id="run-123", category="ai_tokens", estimated_amount=-1.0
        )


def test_capture_cost_entry_infinite_amount():
    """Test that an infinite amount raises a ValueError."""
    with pytest.raises(ValueError, match="must be a finite number"):
        capture_cost_entry(
            run_id="run-123", category="ai_tokens", estimated_amount=float("inf")
        )


def test_capture_cost_entry_oversized_field():
    """Test that an oversized string field raises a ValueError."""
    with pytest.raises(ValueError, match="exceeds maximum length"):
        capture_cost_entry(run_id="a" * 129, category="ai_tokens", estimated_amount=1.0)


@pytest.mark.parametrize(
    "forbidden_value",
    [
        "550e8400-e29b-41d4-a716-446655440000",  # GUID
        "/subscriptions/123-456",  # Resource ID
        "AccountKey=supersecret",  # Secret
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",  # Token
    ],
)
def test_capture_cost_entry_forbidden_fields(forbidden_value):
    """Test that forbidden technical/billing info raises a ValueError."""
    with pytest.raises(
        ValueError, match="contains forbidden technical or billing information"
    ):
        capture_cost_entry(
            run_id=forbidden_value, category="ai_tokens", estimated_amount=1.0
        )


def test_capture_cost_entry_unknown_fields():
    """Test that extra fields not in schema are rejected (if passed via kwargs somehow).
    Since capture_cost_entry has explicit arguments, we test the schema validation
    by manually triggering it if we ever change to **kwargs.
    For now, verifying that the schema has additionalProperties: false is part of contract tests.
    """
    # The current implementation uses explicit arguments, so unknown fields
    # would be a TypeError at the Python level.
    with pytest.raises(TypeError):
        capture_cost_entry(
            run_id="run-123",
            category="ai_tokens",
            estimated_amount=1.0,
            unknown_field="boom",
        )
