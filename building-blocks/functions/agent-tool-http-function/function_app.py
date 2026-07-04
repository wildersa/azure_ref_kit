import azure.functions as func
import logging
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="system_status", methods=["GET"])
def get_system_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    Returns the current operational status of the system.
    This is a safe, read-only tool boundary example.
    """
    logging.info('System status tool invoked.')

    # Example of a safe, bounded response schema
    # Avoids exposing raw logs, internal stack traces, or credentials.
    status_result = {
        "business_status": "operational",
        "service_health": "healthy",
        "active_regions": ["eastus", "westus2"],
        "last_updated": "2026-07-03T10:00:00Z",
        "environment": "production-reference"
    }

    return func.HttpResponse(
        body=json.dumps(status_result),
        mimetype="application/json",
        status_code=200
    )
