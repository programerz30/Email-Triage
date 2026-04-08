# app.py - FastAPI server
# This exposes the environment over HTTP so the inference script can call it

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from env import EmailTriageEnv, EmailAction

app = FastAPI(
    title="Email Triage OpenEnv",
    description="An OpenEnv environment for AI agent email triage tasks.",
    version="1.0.0"
)

# Store one environment instance per task
# In production you'd use sessions, but this is fine for hackathon
environments = {}


# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_name: Optional[str] = "task1_categorize"
    task: Optional[str] = None  # alias used by inference.py

class StepRequest(BaseModel):
    task_name: Optional[str] = "task1_categorize"
    task: Optional[str] = None
    text: str = ""  # The agent's response


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "environment": "EmailTriageEnv",
        "tasks": ["task1_categorize", "task2_prioritize", "task3_full_triage"]
    }

@app.get("/health")
def health():
    """Health check for HF Space ping."""
    return {"status": "ok"}


@app.post("/reset")
def reset(request: Optional[ResetRequest] = None):
    """
    Start a new episode.
    Called at the beginning of every task run.
    """
    if request is None:
        task_name = "task1_categorize"
    else:
        # Support both 'task' and 'task_name' fields
        task_name = request.task or request.task_name or "task1_categorize"
    try:
        env = EmailTriageEnv(task_name=task_name)
        environments[task_name] = env
        result = env.reset()
        return result.dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(request: StepRequest):
    """
    Agent takes a step (submits a response).
    Returns observation, reward, done, info.
    """
    task_name = request.task or request.task_name or "task1_categorize"

    if task_name not in environments:
        raise HTTPException(
            status_code=400,
            detail=f"No active episode for task '{task_name}'. Call /reset first."
        )

    env = environments[task_name]
    action = EmailAction(text=request.text)
    result = env.step(action)
    return result.dict()


@app.get("/state")
def state(task_name: str = "task1_categorize"):
    """
    Return the current internal state of the environment.
    """
    if task_name not in environments:
        raise HTTPException(
            status_code=400,
            detail=f"No active episode for task '{task_name}'. Call /reset first."
        )
    return environments[task_name].state()


@app.get("/tasks")
def list_tasks():
    """List all available tasks with descriptions."""
    from tasks import TASKS
    return {
        name: {
            "description": t["description"],
            "difficulty": t["difficulty"],
            "max_steps": t["max_steps"],
        }
        for name, t in TASKS.items()
    }


def main():
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()
