from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.orchestrator import ask

router = APIRouter()


class StrategyQuery(BaseModel):
    question: str


@router.post("/ask")
def ask_strategy_advisor(query: StrategyQuery):
    """
    Entry point for the AI Executive Copilot.
    Routes the question through the Orchestrator Agent (LangGraph):
    Research Agent (Knowledge Graph) -> Strategy Advisor Agent (LLM reasoning).
    """
    return ask(query.question)