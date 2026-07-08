from fastapi import FastAPI
from pydantic import BaseModel, Field
from datetime import datetime, UTC

app = FastAPI(title="Container-hosted Agent API")


class AgentStatusResponse(BaseModel):
    status: str = Field(..., description="The current status of the agent task")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    summary: str = Field(..., description="A customer-safe summary of the progress")


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}


@app.get("/status/{task_id}", response_model=AgentStatusResponse)
async def get_status(task_id: str):
    # This is a stub implementation for the reference hosting block
    return AgentStatusResponse(
        status="running",
        summary=f"Agent is processing task {task_id}. Technical details are redacted.",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
