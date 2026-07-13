from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from src.models import (
    GetPipelineRunStatusRequest,
    GetPipelineRunStatusResponse,
    PipelineStatus,
    PipelineResult,
    ListRecentPipelineRunsRequest,
    ListRecentPipelineRunsResponse,
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


def test_list_recent_pipeline_runs_request_valid():
    """Verify valid list request."""
    req = ListRecentPipelineRunsRequest(pipeline_id="Main-CI", top=10, branch="main")
    assert req.pipeline_id == "Main-CI"
    assert req.top == 10
    assert req.branch == "main"


def test_list_recent_pipeline_runs_request_default():
    """Verify default value for top."""
    req = ListRecentPipelineRunsRequest(pipeline_id="Main-CI")
    assert req.top == 5
    assert req.branch is None


def test_list_recent_pipeline_runs_request_invalid_top():
    """Verify constraints on top field."""
    with pytest.raises(ValidationError):
        ListRecentPipelineRunsRequest(pipeline_id="Main-CI", top=0)
    with pytest.raises(ValidationError):
        ListRecentPipelineRunsRequest(pipeline_id="Main-CI", top=21)


def test_list_recent_pipeline_runs_response_valid():
    """Verify valid list response."""
    now = datetime.now(timezone.utc)
    res = ListRecentPipelineRunsResponse(
        pipeline_name="Main CI",
        runs=[
            {
                "run_id": "1",
                "status": PipelineStatus.COMPLETED,
                "result": PipelineResult.SUCCEEDED,
                "branch": "main",
                "start_time": now,
            }
        ],
    )
    assert len(res.runs) == 1
    assert res.runs[0].run_id == "1"
