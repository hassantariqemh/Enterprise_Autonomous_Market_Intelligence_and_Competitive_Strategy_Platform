"""
Generates a structured SWOT analysis for a company using data pulled from
the Knowledge Graph (products, events, review sentiment) combined with an
LLM (Groq) for reasoning, with source evidence attached to each point.
"""
import os
import json
from langchain_groq import ChatGroq
from app.utils.neo4j_connection import db

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    groq_api_key=os.getenv("GROQ_API_KEY"),
)


def gather_company_facts(company: str) -> dict:
    products = db.run_query(
        "MATCH (c:Company {name: $company})-[:LAUNCHED]->(p:Product) "
        "RETURN p.name AS name, p.category AS category, p.price AS price",
        {"company": company},
    )

    events = db.run_query(
        "MATCH (c:Company {name: $company})-[:INVOLVED_IN]->(e:Event) "
        "RETURN e.type AS type, e.date AS date, e.description AS description",
        {"company": company},
    )

    reviews = db.run_query(
        "MATCH (c:Company {name: $company})-[:LAUNCHED]->(p:Product)<-[:REVIEWS]-(r:Review) "
        "RETURN p.name AS product, r.rating AS rating, r.sentiment AS sentiment, r.text AS text",
        {"company": company},
    )

    return {"products": products, "events": events, "reviews": reviews}


def build_prompt(company: str, facts: dict) -> str:
    return f"""
You are a market intelligence analyst. Based ONLY on the evidence below,
produce a SWOT analysis for {company}.

PRODUCTS:
{json.dumps(facts['products'], indent=2, default=str)}

MARKET EVENTS:
{json.dumps(facts['events'], indent=2, default=str)}

CUSTOMER REVIEW SIGNALS:
{json.dumps(facts['reviews'], indent=2, default=str)}

Return ONLY valid JSON in this exact structure, with no extra text:
{{
  "company": "{company}",
  "strengths": [{{"point": "...", "evidence": "..."}}],
  "weaknesses": [{{"point": "...", "evidence": "..."}}],
  "opportunities": [{{"point": "...", "evidence": "..."}}],
  "threats": [{{"point": "...", "evidence": "..."}}],
  "confidence": "high|medium|low"
}}

Each point must cite specific evidence from the data above (product names,
event descriptions, or review signals). If data is sparse for a category,
say so honestly rather than inventing facts, and set confidence to "low".
"""


def generate_swot(company: str) -> dict:
    facts = gather_company_facts(company)

    if not facts["products"] and not facts["events"] and not facts["reviews"]:
        return {
            "status": "insufficient_data",
            "message": f"No data found for '{company}' in the knowledge graph.",
        }

    prompt = build_prompt(company, facts)
    response = llm.invoke(prompt)

    try:
        swot = json.loads(response.content)
        return {"status": "ok", **swot}
    except json.JSONDecodeError:
        return {
            "status": "parse_error",
            "message": "LLM did not return valid JSON.",
            "raw_response": response.content,
        }