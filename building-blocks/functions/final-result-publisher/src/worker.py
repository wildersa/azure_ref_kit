import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .adapters import ArtifactStoreAdapter, StatusStoreAdapter


def publish_final_result(
    run_id: str,
    validation_status: str,
    artifact_ids: List[str],
    artifact_adapter: ArtifactStoreAdapter,
    status_adapter: StatusStoreAdapter,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Coordinates the final publication of results.
    Marks artifacts as visible and updates the final run status.
    """
    try:
        logging.info(f"Finalizing result for run_id: {run_id}")

        # 1. Update artifact visibility
        for aid in artifact_ids:
            try:
                artifact_adapter.set_visible(run_id, aid)
            except Exception:
                # Safe boundary: avoid logging raw artifact IDs or technical exception strings.
                logging.error(
                    f"Failed to set visibility for one or more artifacts for RunID: {run_id}"
                )
                raise

        # 2. Determine final status and summary
        final_status = "completed"
        business_summary = "Processing complete. Your document data is now available."

        if validation_status == "failed":
            final_status = "failed"
            business_summary = (
                "Processing failed during validation. Please review the errors."
            )
        elif validation_status == "warning":
            business_summary = (
                "Processing complete with warnings. Some fields may require review."
            )

        # 3. Update status store
        finished_at = datetime.now(timezone.utc).isoformat()
        status_adapter.update_run_status(
            run_id=run_id,
            status=final_status,
            business_summary=business_summary,
            finished_at=finished_at,
        )

        return {
            "publication_status": "published",
            "run_id": run_id,
            "status": final_status,
            "business_summary": business_summary,
            "finished_at": finished_at,
        }

    except Exception:
        # Technical details are logged internally by the orchestrator/SDK.
        # Safe boundary: avoid logging raw exception strings or technical details.
        logging.error(f"Final publication failed for RunID: {run_id}")
        return {
            "publication_status": "failed",
            "run_id": run_id,
            "friendly_error": "An internal error occurred during result publication.",
        }
