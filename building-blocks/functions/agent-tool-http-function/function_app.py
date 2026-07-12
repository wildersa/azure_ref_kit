import azure.functions as func
import logging
import json

try:
    from .src.tool import get_resource_info_safe
except ImportError:
    from src.tool import get_resource_info_safe

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="get_resource_info", methods=["POST"])
def get_resource_info_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger for the Resource Info tool.
    Accepts JSON POST requests only.
    """
    logging.info("Python HTTP trigger function processed a request.")

    try:
        # 1. Parse and validate JSON body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON body."}),
                status_code=400,
                mimetype="application/json",
            )

        # 2. Call the safe tool logic
        result = get_resource_info_safe(req_body)

        # 3. Return the sanitized result
        return func.HttpResponse(
            json.dumps(result), status_code=200, mimetype="application/json"
        )

    except ValueError as e:
        # Expected validation errors
        return func.HttpResponse(
            json.dumps({"error": str(e)}), status_code=400, mimetype="application/json"
        )
    except Exception:
        # Unexpected errors are redacted for customer safety
        # P0: Do not log stack traces (logging.exception)
        logging.error("An unhandled exception occurred in the tool boundary.")
        return func.HttpResponse(
            json.dumps({"error": "An internal error occurred while processing the request."}),
            status_code=500,
            mimetype="application/json",
        )
