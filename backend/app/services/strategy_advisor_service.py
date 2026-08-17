"""
AI Strategy Advisor.
Recommends strategic actions (market entry, pricing, product roadmap,
partnerships, investment priorities, competitive response) for a company
based on knowledge graph evidence and LLM reasoning.
"""
import os
import json
from langchain_groq import ChatGroq
from app.utils.neo4j_connection import db

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)


def gather_strategy_context(company: str):
    own_products = db.run_query(
        "MATCH (c:Company {name: $company})-[:LAUNCHED]->(p:Product) "
        "RETURN p.name AS name, p.category AS category, p.price AS price",
        {"company": company},
    )

    competitors = db.run_query(
        "MATCH (c:Company)-[:LAUNCHED]->(p:Product) WHERE c.name <> $company "
        "RETURN c.name AS company, p.name AS product, p.category AS category, p.price AS price",
        {"company": company},
    )

    market_events = db.run_query(
        "MATCH (c:Company)-[:INVOLVED_IN]->(e:Event) "
        "RETURN c.name AS company, e.type AS type, e.description AS description, e.date AS date "
        "ORDER BY e.date DESC",
        {},
    )

    sentiment = db.run_query(
        "MATCH (c:Company {name: $company})-[:LAUNCHED]->(p:Product)<-[:REVIEWS]-(r:Review) "
        "RETURN p.name AS product, avg(r.sentiment) AS avg_sentiment, avg(r.rating) AS avg_rating",
        {"company": company},
    )

    return {
        "own_products": own_products,
        "competitor_products": competitors,
        "market_events": market_events,
        "sentiment": sentiment,
    }


def build_prompt(company: str, context: dict) -> str:
    return f"""
You are an AI Strategy Advisor for {company}'s executive team. Based ONLY
on the market data below, recommend strategic actions.

{company}'S OWN PRODUCTS:
{json.dumps(context['own_products'], indent=2, default=str)}

COMPETITOR PRODUCTS:
{json.dumps(context['competitor_products'], indent=2, default=str)}

RECENT MARKET EVENTS (all companies):
{json.dumps(context['market_events'], indent=2, default=str)}

CUSTOMER SENTIMENT ON {company}'S PRODUCTS:
{json.dumps(context['sentiment'], indent=2, default=str)}

Return ONLY valid JSON (no markdown fences, no extra text) in this exact
structure:
{{
  "company": "{company}",
  "recommendations": [
    {{
      "category": "New Market Entry|Pricing Strategy|Product Roadmap|Partnership Opportunities|Investment Priorities|Competitive Response",
      "recommendation": "...",
      "rationale": "...",
      "evidence": "...",
      "priority": "high|medium|low"
    }}
  ],
  "confidence": "high|medium|low",
  "confidence_reason": "..."
}}

Cover as many of the 6 categories as the data reasonably supports. If data
is too sparse for a category, omit it rather than inventing a recommendation.
"""


def clean_json_response(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return raw


def generate_strategy(company: str) -> dict:
    context = gather_strategy_context(company)

    if not context["own_products"]:
        return {
            "status": "insufficient_data",
            "message": f"No product data found for '{company}' in the knowledge graph.",
        }

    prompt = build_prompt(company, context)
    response = llm.invoke(prompt)
    raw = clean_json_response(response.content)

    try:
        result = json.loads(raw)
        return {"status": "ok", **result}
    except json.JSONDecodeError:
        return {
            "status": "parse_error",
            "message": "LLM did not return valid JSON.",
            "raw_response": response.content,
        }