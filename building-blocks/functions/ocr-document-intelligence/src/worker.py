import json
import logging
import io
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from .adapters import DocumentIntelligenceAdapter, StorageAdapter


def process_ocr_task(
    run_id: str,
    artifact_id: str,
    document_type: str,
    storage_ref: str,
    doc_intel_adapter: DocumentIntelligenceAdapter,
    storage_adapter: StorageAdapter,
    artifact_container: str = "artifacts",
) -> Dict[str, Any]:
    """
    Coordinates the OCR process: downloads document, calls Document Intelligence,
    normalizes output, and saves raw result as a private artifact.
    """
    try:
        logging.info(f"Starting OCR for run_id={run_id}, artifact_id={artifact_id}")

        # 1. Download document
        document_bytes = storage_adapter.download_blob(storage_ref)

        # 2. Analyze document
        analyze_result = doc_intel_adapter.analyze_document(
            model_id=document_type, document=io.BytesIO(document_bytes)
        )

        # 3. Store raw result as private artifact
        raw_result_json = analyze_result.as_dict()
        raw_artifact_id = f"raw-ocr-{uuid.uuid4()}"
        raw_blob_name = f"{run_id}/{raw_artifact_id}.json"

        storage_adapter.upload_blob(
            container=artifact_container,
            blob_name=raw_blob_name,
            data=json.dumps(raw_result_json).encode("utf-8"),
            content_type="application/json",
        )

        # 4. Normalize output for pipeline-step contract
        extracted_text = ""
        if hasattr(analyze_result, "content"):
            extracted_text = analyze_result.content
        elif "content" in raw_result_json:
            extracted_text = raw_result_json["content"]

        fields = {}
        confidences = []

        # Extract fields for prebuilt/custom models
        if hasattr(analyze_result, "documents") and analyze_result.documents:
            for doc in analyze_result.documents:
                if hasattr(doc, "fields") and doc.fields:
                    for field_name, field in doc.fields.items():
                        # Only take simple values for the fields summary
                        value = None
                        if hasattr(field, "value"):
                            value = field.value
                        elif isinstance(field, dict) and "value" in field:
                            value = field["value"]

                        fields[field_name] = str(value) if value is not None else None

                        if hasattr(field, "confidence"):
                            confidences.append(field.confidence)
                        elif isinstance(field, dict) and "confidence" in field:
                            confidences.append(field["confidence"])

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "run_id": run_id,
            "name": "ocr-document-intelligence",
            "status": "completed",
            "extracted_text": extracted_text,
            "fields": fields,
            "confidence": avg_confidence,
            "artifacts": [raw_artifact_id],
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception:
        # We explicitly do not log str(e) to avoid leaking secrets, SAS tokens, or internal URLs
        # that are often present in Azure SDK exception messages.
        logging.error(
            f"OCR failed for run_id={run_id}. See Application Insights for technical details."
        )
        # Map to safe failure response
        return {
            "run_id": run_id,
            "name": "ocr-document-intelligence",
            "status": "failed",
            "friendly_error": "Document analysis failed. Please ensure the document is clear and in a supported format.",
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
