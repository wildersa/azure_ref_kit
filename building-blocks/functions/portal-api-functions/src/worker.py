import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .adapters import StorageAdapter

# Load schemas
CONTRACTS_PATH = (
    Path(__file__).parent.parent.parent.parent.parent / "shared" / "contracts"
)


def load_schema(filename: str) -> Dict[str, Any]:
    with open(CONTRACTS_PATH / filename, "r") as f:
        return json.load(f)


PIPELINE_RUN_SCHEMA = load_schema("pipeline-run.schema.json")
PIPELINE_STEP_SCHEMA = load_schema("pipeline-step.schema.json")
ARTIFACT_SCHEMA = load_schema("artifact.schema.json")
COST_LEDGER_SCHEMA = load_schema("cost-ledger.schema.json")


class PortalWorker:
    def __init__(self, adapter: StorageAdapter = None):
        self.adapter = adapter or StorageAdapter()

    def _sanitize_run(self, run: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures the run object only contains customer-safe fields."""
        safe_run = {
            "id": run.get("id") or run.get("RowKey"),
            "customer_id": run.get("customer_id") or run.get("PartitionKey"),
            "pipeline_type": run.get("pipeline_type"),
            "status": run.get("status"),
            "current_step": run.get("current_step"),
            "progress_percent": run.get("progress_percent"),
            "business_summary": run.get("business_summary"),
            "friendly_error": run.get("friendly_error"),
            "correlation_id": run.get("correlation_id"),
            "estimated_cost": run.get("estimated_cost"),
            "created_at": run.get("created_at"),
            "started_at": run.get("started_at"),
            "finished_at": run.get("finished_at"),
        }
        # Filter out None values for fields that might not be present but are not required
        return {
            k: v
            for k, v in safe_run.items()
            if v is not None
            or k in ["id", "customer_id", "pipeline_type", "status", "created_at"]
        }

    def _sanitize_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures the step object only contains customer-safe fields."""
        safe_step = {
            "run_id": step.get("run_id") or step.get("PartitionKey"),
            "name": step.get("name") or step.get("RowKey"),
            "status": step.get("status"),
            "input_summary": step.get("input_summary"),
            "output_summary": step.get("output_summary"),
            "friendly_error": step.get("friendly_error"),
            "artifacts": step.get("artifacts"),
            "retry_count": step.get("retry_count"),
            "started_at": step.get("started_at"),
            "finished_at": step.get("finished_at"),
        }
        if isinstance(safe_step["artifacts"], str):
            try:
                safe_step["artifacts"] = json.loads(safe_step["artifacts"])
            except Exception:
                safe_step["artifacts"] = []

        return {
            k: v
            for k, v in safe_step.items()
            if v is not None or k in ["run_id", "name", "status"]
        }

    def get_recent_runs(self, customer_id: str) -> List[Dict[str, Any]]:
        runs = self.adapter.get_runs(customer_id)
        # Sort by created_at descending if possible
        runs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return [self._sanitize_run(r) for r in runs]

    def get_run_detail(self, customer_id: str, run_id: str) -> Optional[Dict[str, Any]]:
        run = self.adapter.get_run(customer_id, run_id)
        if not run:
            return None

        safe_run = self._sanitize_run(run)
        steps = self.adapter.get_steps(run_id)
        # Sort steps by started_at
        steps.sort(key=lambda x: x.get("started_at", ""))

        safe_run["steps"] = [self._sanitize_step(s) for s in steps]
        return safe_run

    def get_artifacts(
        self, customer_id: str, run_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        # First verify the run belongs to the customer
        run = self.adapter.get_run(customer_id, run_id)
        if not run:
            return None

        artifacts = self.adapter.get_artifacts(run_id)

        # Map to customer-safe artifact identifier/download route shape
        safe_artifacts = []
        for art in artifacts:
            art_id = art.get("id")
            safe_artifacts.append(
                {
                    "id": art_id,
                    "run_id": run_id,
                    "kind": art.get("kind"),
                    "safe_name": art.get("safe_name"),
                    "download_url": f"/api/artifacts/{art_id}/download",
                    "content_type": art.get("content_type"),
                    "size_bytes": art.get("size_bytes"),
                    "is_customer_visible": True,
                    "created_at": art.get("created_at"),
                }
            )

        return safe_artifacts

    def get_cost_summary(
        self, customer_id: str, run_id: str
    ) -> Optional[Dict[str, Any]]:
        # First verify the run belongs to the customer
        run = self.adapter.get_run(customer_id, run_id)
        if not run:
            return None

        costs = self.adapter.get_costs(run_id)
        total_estimated_amount = sum(c.get("estimated_amount", 0) for c in costs)

        return {
            "run_id": run_id,
            "total_estimated_amount": total_estimated_amount,
            "currency": "USD",
            "breakdown": [
                {
                    "category": c.get("category"),
                    "estimated_amount": c.get("estimated_amount"),
                }
                for c in costs
            ],
        }
