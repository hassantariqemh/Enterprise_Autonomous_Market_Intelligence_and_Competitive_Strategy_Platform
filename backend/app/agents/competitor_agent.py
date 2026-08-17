from app.services import competitor_service
from app.utils.neo4j_connection import db


def get_product_pricing():
    return db.run_query(
        "MATCH (c:Company)-[:LAUNCHED]->(p:Product) "
        "RETURN c.name AS company, p.name AS product, p.category AS category, p.price AS price",
        {},
    )


def get_market_events():
    return db.run_query(
        "MATCH (c:Company)-[:INVOLVED_IN]->(e:Event) "
        "RETURN c.name AS company, e.type AS type, e.description AS description, e.date AS date "
        "ORDER BY e.date DESC",
        {},
    )


def get_sentiment_data():
    return db.run_query(
        "MATCH (c:Company)-[:LAUNCHED]->(p:Product)<-[:REVIEWS]-(r:Review) "
        "RETURN c.name AS company, p.name AS product, avg(r.sentiment) AS avg_sentiment, avg(r.rating) AS avg_rating",
        {},
    )


def run(query: str) -> dict:
    """
    Competitor Analysis Agent.
    Pulls structured facts from the Knowledge Graph relevant to the query,
    selecting which data to fetch based on keywords in the question.
    """
    q = query.lower()
    evidence = {
        "companies": competitor_service.get_all_competitors(),
    }

    if any(word in q for word in ["region", "presence", "expand", "geographic", "market entry"]):
        evidence["rankings_by_region_presence"] = competitor_service.companies_by_region_count()

    if any(word in q for word in ["price", "pricing", "cost", "cheap", "expensive", "budget"]):
        evidence["product_pricing"] = get_product_pricing()

    if any(word in q for word in ["event", "launch", "trend", "activity", "growing", "growth", "partnership", "technology"]):
        evidence["market_events"] = get_market_events()

    if any(word in q for word in ["sentiment", "review", "customer", "rating", "satisfaction"]):
        evidence["sentiment_data"] = get_sentiment_data()

    # Fallback: if no keyword matched, give broad context so the answer isn't empty
    if len(evidence) == 1:
        evidence["rankings_by_region_presence"] = competitor_service.companies_by_region_count()
        evidence["product_pricing"] = get_product_pricing()

    return evidence