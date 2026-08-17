from fastapi import APIRouter
from app.services import network_analysis_service

router = APIRouter()


@router.get("/network-analysis/centrality")
def get_centrality():
    """
    Returns competitive centrality rankings using NetworkX graph analysis
    on top of the knowledge graph — shows which competitors are most
    "contested" (overlap with the most rivals across product categories).
    """
    return network_analysis_service.get_competitive_centrality()