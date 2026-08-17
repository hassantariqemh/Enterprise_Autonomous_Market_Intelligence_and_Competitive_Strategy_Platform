"""
Scenario Simulation Engine.
Given a hypothetical market scenario (new competitor entry, price cut,
product launch, etc.), predicts likely business outcomes using knowledge
graph context combined with LLM reasoning.
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


def gather_market_context(company: str = None):
    companies = db.run_query(
        "MATCH (c:Company) OPTIONAL MATCH (c)-[:LAUNCHED]->(p:Product) "
        "RETURN c.name AS company, collect(p.name) AS products, "
        "collect(p.price) AS prices",
        {},
    )

    events = db.run_query(
        "MATCH (c:Company)-[:INVOLVED_IN]->(e:Event) "
        "RETURN c.name AS company, e.type AS type, e.description AS description, e.date AS date "
        "ORDER BY e.date DESC",
        {},
    )

    focus_products = []
    if company:
        focus_products = db.run_query(
            "MATCH (c:Company {name: $company})-[:LAUNCHED]->(p:Product) "
            "RETURN p.name AS name, p.price AS price, p.category AS category",
            {"company": company},
        )

    return {"companies": companies, "recent_events": events, "focus_company_products": focus_products}


def build_prompt(scenario: str, company: str, context: dict) -> str:
    return f"""
You are a market intelligence analyst running a scenario simulation for
executives. Analyze ONLY based on the market context provided below.

SCENARIO TO SIMULATE:
"{scenario}"
{f'(Primarily concerning: {company})' if company else ''}

CURRENT MARKET LANDSCAPE:
{json.dumps(context['companies'], indent=2, default=str)}

RECENT COMPETITOR EVENTS:
{json.dumps(context['recent_events'], indent=2, default=str)}

{f"FOCUS COMPANY'S PRODUCTS: {json.dumps(context['focus_company_products'], indent=2, default=str)}" if context['focus_company_products'] else ''}

Predict the likely business outcomes of this scenario. Return ONLY valid
JSON in this exact structure, with no extra text:
{{
  "scenario": "{scenario}",
  "predicted_impacts": [
    {{"area": "e.g. Market Share / Pricing / Competitor Response",
      "prediction": "...", "reasoning": "...", "severity": "high|medium|low"}}
  ],
  "recommended_response": ["...", "..."],
  "confidence": "high|medium|low",
  "confidence_reason": "..."
}}

Base every prediction on the market data given above. If the data is too
sparse to predict a given area confidently, say so explicitly rather than
inventing outcomes, and reflect that in the confidence field.
"""


def simulate_scenario(scenario: str, company: str = None) -> dict:
    context = gather_market_context(company)
    prompt = build_prompt(scenario, company, context)
    response = llm.invoke(prompt)

    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
        return {"status": "ok", **result}
    except json.JSONDecodeError:
        return {
            "status": "parse_error",
            "message": "LLM did not return valid JSON.",
            "raw_response": response.content,
        }