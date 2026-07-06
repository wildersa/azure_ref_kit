import azure.functions as func
import azure.durable_functions as df
import os
import logging
from .src.worker import process_ocr_task
from .src.adapters import AzureDocumentIntelligenceAdapter, AzureStorageAdapter

app = df.DFApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.activity_trigger(input_name="inputData")
def ocr_document_intelligence(inputData: dict):
    """
    Durable Functions Activity for OCR using Azure AI Document Intelligence.
    Expects inputData with: run_id, artifact_id, document_type, storage_ref.
    """
    run_id = inputData.get("run_id")
    artifact_id = inputData.get("artifact_id")
    document_type = inputData.get("document_type", "prebuilt-read")
    storage_ref = inputData.get("storage_ref")

    if not all([run_id, artifact_id, storage_ref]):
        return {
            "run_id": run_id,
            "name": "ocr-document-intelligence",
            "status": "failed",
            "friendly_error": "Missing mandatory input data (run_id, artifact_id, or storage_ref).",
        }

    # Configuration from environment
    doc_intel_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    storage_account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")

    if not doc_intel_endpoint or not storage_account_url:
        logging.error(
            "Missing configuration: AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT or AZURE_STORAGE_ACCOUNT_URL"
        )
        return {
            "run_id": run_id,
            "name": "ocr-document-intelligence",
            "status": "failed",
            "friendly_error": "Worker configuration error. Please contact support.",
        }

    # Initialize adapters
    doc_intel_adapter = AzureDocumentIntelligenceAdapter(endpoint=doc_intel_endpoint)
    storage_adapter = AzureStorageAdapter(account_url=storage_account_url)

    # Call core logic
    return process_ocr_task(
        run_id=run_id,
        artifact_id=artifact_id,
        document_type=document_type,
        storage_ref=storage_ref,
        doc_intel_adapter=doc_intel_adapter,
        storage_adapter=storage_adapter,
    )
