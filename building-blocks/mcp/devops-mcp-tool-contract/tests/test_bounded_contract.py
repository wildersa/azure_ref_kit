import pytest
from pydantic import ValidationError
from src.models import GetPipelineRunStatusResponse, PipelineStatus, PipelineResult
from datetime import datetime, timezone

def test_response_pipeline_name_constraints():
    """Verify pipeline_name length and pattern constraints."""
    base_data = {
        "pipeline_name": "Main CI",
        "run_id": "123",
        "status": PipelineStatus.COMPLETED,
        "result": PipelineResult.SUCCEEDED,
        "branch": "main",
        "start_time": datetime.now(timezone.utc)
    }

    # Valid
    GetPipelineRunStatusResponse(**base_data)

    # Invalid pattern (path traversal)
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "pipeline_name": "../../etc/passwd"})

    # Too long
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "pipeline_name": "a" * 129})

def test_response_commit_sha_constraints():
    """Verify commit_sha pattern and length."""
    base_data = {
        "pipeline_name": "Main CI",
        "run_id": "123",
        "status": PipelineStatus.COMPLETED,
        "result": PipelineResult.SUCCEEDED,
        "branch": "main",
        "start_time": datetime.now(timezone.utc)
    }

    # Valid 7 chars
    GetPipelineRunStatusResponse(**{**base_data, "commit_sha": "a1b2c3d"})
    # Valid 8 chars
    GetPipelineRunStatusResponse(**{**base_data, "commit_sha": "a1b2c3d4"})

    # Invalid length (6)
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "commit_sha": "a1b2c3"})
    # Invalid length (9)
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "commit_sha": "a1b2c3d4e"})
    # Invalid characters (non-hex)
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "commit_sha": "g1b2c3d"})

def test_response_duration_seconds_constraints():
    """Verify duration_seconds range."""
    base_data = {
        "pipeline_name": "Main CI",
        "run_id": "123",
        "status": PipelineStatus.COMPLETED,
        "result": PipelineResult.SUCCEEDED,
        "branch": "main",
        "start_time": datetime.now(timezone.utc)
    }

    # Valid
    GetPipelineRunStatusResponse(**{**base_data, "duration_seconds": 3600})

    # Negative
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "duration_seconds": -1})
    # Too large (over 10 days)
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "duration_seconds": 864001})

def test_response_summary_constraints():
    """Verify summary pattern and length."""
    base_data = {
        "pipeline_name": "Main CI",
        "run_id": "123",
        "status": PipelineStatus.COMPLETED,
        "result": PipelineResult.SUCCEEDED,
        "branch": "main",
        "start_time": datetime.now(timezone.utc)
    }

    # Valid
    GetPipelineRunStatusResponse(**{**base_data, "summary": "Build succeeded!"})

    # Too long
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "summary": "a" * 513})
    # Invalid characters (e.g. angle brackets)
    with pytest.raises(ValidationError):
        GetPipelineRunStatusResponse(**{**base_data, "summary": "<script>alert(1)</script>"})
