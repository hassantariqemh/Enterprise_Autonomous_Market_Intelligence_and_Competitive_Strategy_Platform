import json
from fastapi import APIRouter
from app.services import dashboard_service
from app.utils.redis_connection import redis_client

router = APIRouter()

CACHE_KEY = "dashboard:latest"
CACHE_TTL_SECONDS = 60  # near-real-time: cache expires after 1 minute


@router.get("/dashboard")
def get_dashboard():
    """
    Returns aggregated data for the Executive Dashboard:
    market share, competitor activity, sentiment, and forecast.
    Cached in Redis for near-real-time performance (spec NFR requirement),
    with a short TTL so data still refreshes periodically.
    """
    cached = redis_client.get(CACHE_KEY)
    if cached:
        data = json.loads(cached)
        data["_cache"] = "hit"
        return data

    data = dashboard_service.get_dashboard_data()
    redis_client.setex(CACHE_KEY, CACHE_TTL_SECONDS, json.dumps(data, default=str))
    data["_cache"] = "miss"
    return data