import pytest
import json
import base64
from unittest.mock import MagicMock, patch
import azure.functions as func
from function_app import get_runs, get_run_detail, get_artifacts, get_cost


@pytest.fixture
def mock_req():
    req = MagicMock(spec=func.HttpRequest)
    req.headers = {}
    req.route_params = {}
    return req


def test_api_unauthorized(mock_req):
    # Execute
    res = get_runs(mock_req)

    # Assert
    assert res.status_code == 401
    body = json.loads(res.get_body())
    assert body["error"]["code"] == "Unauthorized"


@patch("function_app.PortalWorker")
@patch.dict("os.environ", {"AZURE_FUNCTIONS_ENVIRONMENT": "Development"})
def test_get_runs_success(mock_worker_class, mock_req):
    # Setup
    mock_req.headers["x-dev-customer-id"] = "cust-1"
    mock_worker = mock_worker_class.return_value
    mock_worker.get_recent_runs.return_value = [{"id": "run-1"}]

    # Execute
    res = get_runs(mock_req)

    # Assert
    assert res.status_code == 200
    assert json.loads(res.get_body()) == [{"id": "run-1"}]
    mock_worker.get_recent_runs.assert_called_once_with("cust-1")


@patch("function_app.PortalWorker")
@patch.dict("os.environ", {"AZURE_FUNCTIONS_ENVIRONMENT": "Development"})
def test_get_run_detail_not_found(mock_worker_class, mock_req):
    # Setup
    mock_req.headers["x-dev-customer-id"] = "cust-1"
    mock_req.route_params["runId"] = "run-999"
    mock_worker = mock_worker_class.return_value
    mock_worker.get_run_detail.return_value = None

    # Execute
    res = get_run_detail(mock_req)

    # Assert
    assert res.status_code == 404
    body = json.loads(res.get_body())
    assert body["error"]["code"] == "NotFound"


def test_get_customer_id_from_swa_header(mock_req):
    # Setup
    principal = {"userId": "user-123", "userRoles": ["authenticated"]}
    principal_b64 = base64.b64encode(json.dumps(principal).encode("utf-8")).decode(
        "utf-8"
    )
    mock_req.headers["x-ms-client-principal"] = principal_b64

    # Import locally to use the function under test
    from function_app import get_customer_id

    # Execute
    customer_id = get_customer_id(mock_req)

    # Assert
    assert customer_id == "user-123"


@patch("function_app.PortalWorker")
@patch.dict("os.environ", {"AZURE_FUNCTIONS_ENVIRONMENT": "Development"})
def test_get_artifacts_success(mock_worker_class, mock_req):
    # Setup
    mock_req.headers["x-dev-customer-id"] = "cust-1"
    mock_req.route_params["runId"] = "run-1"
    mock_worker = mock_worker_class.return_value
    mock_worker.get_artifacts.return_value = [{"id": "art-1"}]

    # Execute
    res = get_artifacts(mock_req)

    # Assert
    assert res.status_code == 200
    assert json.loads(res.get_body()) == [{"id": "art-1"}]


@patch("function_app.PortalWorker")
@patch.dict("os.environ", {"AZURE_FUNCTIONS_ENVIRONMENT": "Development"})
def test_get_cost_success(mock_worker_class, mock_req):
    # Setup
    mock_req.headers["x-dev-customer-id"] = "cust-1"
    mock_req.route_params["runId"] = "run-1"
    mock_worker = mock_worker_class.return_value
    mock_worker.get_cost_summary.return_value = {"total_estimated_amount": 0.10}

    # Execute
    res = get_cost(mock_req)

    # Assert
    assert res.status_code == 200
    assert json.loads(res.get_body())["total_estimated_amount"] == 0.10
