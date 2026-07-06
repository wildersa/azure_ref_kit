import azure.durable_functions as df
import logging
import os
from .src.worker import validate_fields
from .src.adapters import StorageAdapter

app = df.DFApp()


@app.activity_trigger(input_name="input")
async def field_validation_worker(input: dict):
    """
    Durable Functions Activity that validates extracted fields.
    """
    run_id = input.get("run_id")
    artifact_id = input.get("artifact_id")
    ruleset_id = input.get("ruleset_id")

    logging.info(
        f"Field validation worker started for RunID: {run_id}, ArtifactID: {artifact_id}"
    )

    if not run_id or not artifact_id:
        error_msg = "Missing mandatory input: run_id and artifact_id are required."
        logging.error(error_msg)
        return {
            "run_id": run_id,
            "name": "field-validation-worker",
            "status": "failed",
            "friendly_error": error_msg,
        }

    try:
        # 1. Initialize Adapters
        connection_string = os.environ.get("BlobStorageConnectionString")
        storage = StorageAdapter(connection_string=connection_string)

        # 2. Load Ruleset (Mocking static ruleset for now as per requirements)
        # In a real scenario, this might be loaded from a database or storage
        ruleset = _get_ruleset(ruleset_id)

        # 3. Read OCR Artifact
        # Assumption: artifacts are in a container named 'artifacts'
        container_name = os.environ.get("ARTIFACT_CONTAINER_NAME", "artifacts")
        blob_name = f"{run_id}/{artifact_id}.json"

        try:
            extracted_data = storage.read_artifact(container_name, blob_name)
        except Exception as e:
            logging.error(f"Failed to read artifact {blob_name}: {str(e)}")
            return {
                "run_id": run_id,
                "name": "field-validation-worker",
                "status": "failed",
                "friendly_error": "Could not find or read the extracted data artifact.",
            }

        # 4. Validate Fields
        report = validate_fields(extracted_data, ruleset)

        # 5. Output Result
        result = report.to_dict()
        result.update(
            {
                "run_id": run_id,
                "name": "field-validation-worker",
                "status": "completed" if report.status != "invalid" else "failed",
                "friendly_error": None
                if report.status != "invalid"
                else "Validation failed for one or more fields.",
            }
        )

        # Safe boundary: ensure result does not contain raw OCR data or internal URLs
        # validate_fields logic already produces a safe report.

        logging.info(
            f"Field validation completed for RunID: {run_id} with status: {report.status}"
        )
        return result

    except Exception as e:
        logging.exception(f"Unexpected error in field-validation-worker: {str(e)}")
        return {
            "run_id": run_id,
            "name": "field-validation-worker",
            "status": "failed",
            "friendly_error": "An internal error occurred during validation.",
        }


def _get_ruleset(ruleset_id: str) -> dict:
    """
    Returns a static ruleset.
    Deterministic and local for this implementation.
    """
    # Example ruleset
    return {
        "required_fields": ["total_amount", "invoice_date", "vendor_name"],
        "confidence_threshold": 0.6,
        "field_types": {
            "total_amount": "number",
            "invoice_date": "date",
            "vendor_name": "string",
        },
    }
