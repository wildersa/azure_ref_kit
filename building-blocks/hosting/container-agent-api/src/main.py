from typing import Annotated
from fastapi import FastAPI, Path
from pydantic import BaseModel, Field, ConfigDict, StringConstraints
from datetime import datetime, UTC

app = FastAPI(title="Container-hosted Agent API")

# Narrow validation for identifiers to prevent injection and reflection
TaskId = Annotated[
    str, StringConstraints(pattern=r"^[a-zA-Z0-9_-]+$", min_length=1, max_length=64)
]


class AgentStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="The current status of the agent task")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    summary: str = Field(..., description="A customer-safe summary of the progress")


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}


@app.get("/status/{task_id}", response_model=AgentStatusResponse)
async def get_status(
    task_id: Annotated[TaskId, Path(description="The unique identifier for the task")],
):
    # This is a stub implementation for the reference hosting block.
    # We explicitly avoid reflecting the task_id in the summary to maintain a safe boundary.
    return AgentStatusResponse(
        status="running",
        summary="The requested agent task is currently being processed. Technical details are redacted.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
