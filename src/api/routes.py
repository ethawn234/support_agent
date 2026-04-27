from fastapi import APIRouter
from agent.state import AgentState

router = APIRouter(prefix="/api/v1")

@router.get("/")
def root() -> dict:
    return {"message": "Agentic Support Assistant API is running."}