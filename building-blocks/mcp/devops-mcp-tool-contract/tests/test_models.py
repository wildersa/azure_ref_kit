from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from src.models import (
    GetPipelineRunStatusRequest,
    GetPipelineRunStatusResponse,
    PipelineStatus,
    PipelineResult,
)


def test_get_pipeline_run_status_request_valid():
    """Verify valid request model."""
    req = GetPipelineRunStatusRequest(pipeline_id="Main-CI", run_id="20240101.1")
    assert req.pipeline_id == "Main-CI"
    assert req.run_id == "20240101.1"


def test_get_pipeline_run_status_request_invalid_identifier():
    """Verify identifier constraints (no path characters)."""
    with pytest.raises(ValidationError):
        GetPipelineRunStatusRequest(pipeline_id="../../secret", run_id="123")


def test_get_pipeline_run_status_request_extra_forbid():
    """Verify extra fields are forbidden."""
    with pytest.raises(ValidationError):
        GetPipelineRunStatusRequest(pipeline_id="123", run_id="456", token="secret")


def test_get_pipeline_run_status_response_valid():
    """Verify valid response model."""
    now = datetime.now(timezone.utc)
    res = GetPipelineRunStatusResponse(
        pipeline_name="Main CI",
        run_id="12345",
        status=PipelineStatus.COMPLETED,
        result=PipelineResult.SUCCEEDED,
        branch="main",
        start_time=now,
        portal_url="https://dev.azure.com/org/proj/_build/results?buildId=12345",
    )
    assert res.status == "completed"
    assert res.result == "succeeded"
    assert res.start_time == now


def test_get_pipeline_run_status_response_invalid_url():
    """Verify response model rejects invalid URL."""
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(
            pipeline_name="Main CI",
            run_id="12345",
            status=PipelineStatus.COMPLETED,
            result=PipelineResult.SUCCEEDED,
            branch="main",
            start_time=datetime.now(timezone.utc),
            portal_url="not-a-url",
        )
