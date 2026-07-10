import azure.functions as func
import logging
from datetime import datetime, timezone

try:
    from .src.models import SystemStatusResponse, ErrorResponse
except ImportError:
    from src.models import SystemStatusResponse, ErrorResponse

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="system_status", methods=["GET"])
def get_system_status(req: func.HttpRequest) -> func.HttpResponse:
    """
    Returns the current operational status of the system.
    This is a safe, read-only tool boundary example using Pydantic for validation.
    """
    logging.info("System status tool invoked.")

    try:
        # Example of a safe, bounded response schema
        # In a real scenario, this would fetch data from a database or service.
        status_data = {
            "business_status": "operational",
            "service_health": "healthy",
            "active_regions": ["eastus", "westus2"],
            "last_updated": datetime.now(timezone.utc),
            "environment": "production-reference",
        }

        # Use Pydantic for deterministic validation and serialization
        response_model = SystemStatusResponse(**status_data)

        return func.HttpResponse(
            body=response_model.model_dump_json(),
            mimetype="application/json",
            status_code=200,
        )

    except Exception:
        # Standardized customer-safe logging boundary: do not log str(e) or raw exception objects.
        # This prevents leaking secrets, tokens, internal URLs, or provider internals in logs.
        logging.error("An unexpected error occurred in the system status tool.")

        # Return a customer-safe, friendly error message
        error_response = ErrorResponse(
            error_code="INTERNAL_ERROR",
            friendly_message="An internal error occurred while retrieving system status.",
        )

        return func.HttpResponse(
            body=error_response.model_dump_json(),
            mimetype="application/json",
            status_code=500,
        )
