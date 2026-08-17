from fastapi import APIRouter, HTTPException
from app.services import competitor_service

router = APIRouter()


@router.get("/")
def list_competitors():
    """
    Returns all tracked competitors from the Knowledge Graph.
    """
    return {"competitors": competitor_service.get_all_competitors()}


@router.get("/rankings/by-region-presence")
def rankings_by_region_presence():
    """
    Returns competitors ranked by number of regions they operate in.
    """
    return {"rankings": competitor_service.companies_by_region_count()}


@router.get("/{competitor_name}")
def get_competitor_profile(competitor_name: str):
    """
    Returns intelligence profile for a single competitor,
    including the regions it operates in.
    """
    profile = competitor_service.get_competitor_profile(competitor_name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Competitor '{competitor_name}' not found")
    return profile