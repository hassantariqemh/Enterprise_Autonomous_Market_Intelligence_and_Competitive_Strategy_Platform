import json
from fastapi import APIRouter
from app.agents import forecast_agent
from app.utils.redis_connection import redis_client

router = APIRouter()

CACHE_TTL_SECONDS = 600


@router.get("/trend")
def get_overall_trend():
    cache_key = "forecast:overall"
    cached = redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["_cache"] = "hit"
        return data

    data = forecast_agent.run()
    redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(data, default=str))
    data["_cache"] = "miss"
    return data


@router.get("/trend/{competitor_name}")
def get_trend_forecast(competitor_name: str):
    cache_key = f"forecast:{competitor_name.lower()}"
    cached = redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["_cache"] = "hit"
        return data

    data = forecast_agent.run(company=competitor_name)
    redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(data, default=str))
    data["_cache"] = "miss"
    return data