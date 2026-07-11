from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class Artifact(BaseModel):
    """
    Represents an artifact stored in the blob store, aligned with
    shared/contracts/artifact.schema.json.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    run_id: str
    step_name: Optional[str] = None
    kind: str
    safe_name: str
    storage_ref: str
    content_type: Optional[str] = None
    size_bytes: Optional[int] = Field(None, ge=0)
    is_customer_visible: bool = False
    created_at: Optional[str] = None
