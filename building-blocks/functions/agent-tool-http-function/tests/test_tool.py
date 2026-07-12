import pytest
from src.tool import get_resource_info, get_resource_info_safe
from src.models import ResourceStatus, ResourceType


def test_get_resource_info_success():
    """Test successful resource info retrieval."""
    request_params = {
        "resource_id": "vm-prod-a",  # ends in 'a' -> RUNNING
        "resource_type": "virtual_machine",
    }
    response = get_resource_info(request_params)

    assert response.resource_id == "vm-prod-a"
    assert response.resource_type == ResourceType.VIRTUAL_MACHINE
    assert response.status == ResourceStatus.RUNNING
    assert response.location == "northeurope"  # 'v' is not in a-l
    assert "is currently running" in response.summary


def test_get_resource_info_status_mapping():
    """Test deterministic status mapping logic."""
    # Ends in 'f' -> STOPPED
    res_f = get_resource_info({"resource_id": "res-f", "resource_type": "database"})
    assert res_f.status == ResourceStatus.STOPPED

    # Ends in 'k' -> DEGRADED
    res_k = get_resource_info(
        {"resource_id": "res-k", "resource_type": "storage_account"}
    )
    assert res_k.status == ResourceStatus.DEGRADED

    # Ends in 'z' -> UNKNOWN
    res_z = get_resource_info({"resource_id": "res-z", "resource_type": "database"})
    assert res_z.status == ResourceStatus.UNKNOWN


def test_get_resource_info_invalid_input():
    """Test validation with invalid input."""
    # Missing required field
    with pytest.raises(ValueError, match="Invalid request parameters"):
        get_resource_info({"resource_id": "missing-type"})

    # Invalid enum value
    with pytest.raises(ValueError, match="Invalid request parameters"):
        get_resource_info({"resource_id": "res-1", "resource_type": "invalid_type"})


def test_get_resource_info_safe():
    """Test the safe entrypoint returns a dict."""
    request_params = {"resource_id": "vm-1", "resource_type": "virtual_machine"}
    result = get_resource_info_safe(request_params)
    assert isinstance(result, dict)
    assert result["resource_id"] == "vm-1"
    assert "status" in result
