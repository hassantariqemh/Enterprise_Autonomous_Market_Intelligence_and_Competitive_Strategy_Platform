import json
from fastapi import APIRouter
from app.agents import swot_agent
from app.utils.redis_connection import redis_client

router = APIRouter()

CACHE_TTL_SECONDS = 600  # 10 minutes — LLM calls are expensive, cache longer


@router.get("/swot/{company_name}")
def get_swot(company_name: str):
    cache_key = f"swot:{company_name.lower()}"
    cached = redis_client.get(cache_key)
    if cached:
        data = json.loads(cached)
        data["_cache"] = "hit"
        return data

    data = swot_agent.run(company_name)
    redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(data, default=str))
    data["_cache"] = "miss"
    return data