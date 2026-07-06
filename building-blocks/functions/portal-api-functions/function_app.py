import azure.functions as func
import logging
import json
import base64

try:
    from .src.worker import PortalWorker
except ImportError:
    from src.worker import PortalWorker

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def get_customer_id(req: func.HttpRequest) -> str:
    """
    Extracts the customer_id from the Static Web Apps client principal header.
    Falls back to a header for local development/testing if configured.
    """
    # 1. Try SWA Principal Header
    principal_header = req.headers.get("x-ms-client-principal")
    if principal_header:
        try:
            decoded_principal = json.loads(
                base64.b64decode(principal_header).decode("utf-8")
            )
            # SWA typically provides 'userId' or we can use 'userDetails' (email/id)
            # In our system, we map the identity provider's ID to our customer_id
            return decoded_principal.get("userId")
        except Exception as e:
            logging.error(f"Failed to decode x-ms-client-principal: {str(e)}")

    # 2. Fallback for development (DO NOT USE IN PRODUCTION without proper guards)
    # In a real scenario, this would be guarded by environment checks
    dev_customer_id = req.headers.get("x-dev-customer-id")
    if dev_customer_id:
        return dev_customer_id

    return None


def error_response(
    code: str, message: str, status_code: int = 400
) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(
            {
                "error": {
                    "code": code,
                    "message": message,
                    "correlation_id": "opaque-reference-id",  # In real app, use actual correlation ID
                }
            }
        ),
        status_code=status_code,
        mimetype="application/json",
    )


@app.route(route="runs", methods=["GET"])
def get_runs(req: func.HttpRequest) -> func.HttpResponse:
    customer_id = get_customer_id(req)
    if not customer_id:
        return error_response(
            "Unauthorized", "Missing or invalid customer identity.", 401
        )

    worker = PortalWorker()
    runs = worker.get_recent_runs(customer_id)
    return func.HttpResponse(json.dumps(runs), mimetype="application/json")


@app.route(route="runs/{runId}", methods=["GET"])
def get_run_detail(req: func.HttpRequest) -> func.HttpResponse:
    customer_id = get_customer_id(req)
    if not customer_id:
        return error_response(
            "Unauthorized", "Missing or invalid customer identity.", 401
        )

    run_id = req.route_params.get("runId")
    worker = PortalWorker()
    run = worker.get_run_detail(customer_id, run_id)

    if not run:
        return error_response(
            "NotFound", "Pipeline run not found or access denied.", 404
        )

    return func.HttpResponse(json.dumps(run), mimetype="application/json")


@app.route(route="runs/{runId}/artifacts", methods=["GET"])
def get_artifacts(req: func.HttpRequest) -> func.HttpResponse:
    customer_id = get_customer_id(req)
    if not customer_id:
        return error_response(
            "Unauthorized", "Missing or invalid customer identity.", 401
        )

    run_id = req.route_params.get("runId")
    worker = PortalWorker()
    artifacts = worker.get_artifacts(customer_id, run_id)

    if artifacts is None:
        return error_response(
            "NotFound", "Pipeline run not found or access denied.", 404
        )

    return func.HttpResponse(json.dumps(artifacts), mimetype="application/json")


@app.route(route="runs/{runId}/cost", methods=["GET"])
def get_cost(req: func.HttpRequest) -> func.HttpResponse:
    customer_id = get_customer_id(req)
    if not customer_id:
        return error_response(
            "Unauthorized", "Missing or invalid customer identity.", 401
        )

    run_id = req.route_params.get("runId")
    worker = PortalWorker()
    cost_summary = worker.get_cost_summary(customer_id, run_id)

    if cost_summary is None:
        return error_response(
            "NotFound", "Pipeline run not found or access denied.", 404
        )

    return func.HttpResponse(json.dumps(cost_summary), mimetype="application/json")
