from fastapi import APIRouter
from pydantic import BaseModel
from app.agents import scenario_agent

router = APIRouter()


class ScenarioRequest(BaseModel):
    scenario: str
    company: str | None = None


@router.post("/scenario")
def run_scenario(request: ScenarioRequest):
    """
    Simulates a hypothetical market scenario and predicts business outcomes.
    """
    return scenario_agent.run(request.scenario, request.company)