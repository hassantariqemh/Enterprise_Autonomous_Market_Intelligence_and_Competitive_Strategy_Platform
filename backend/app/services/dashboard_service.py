"""
Aggregates data from across the platform (knowledge graph stats, forecasts,
SWOT, sentiment) into a single Executive Dashboard payload.
"""
from app.utils.neo4j_connection import db
from app.services import forecast_service, strategy_advisor_service

KNOWN_COMPANIES = [
    "Samsung", "Apple", "Xiaomi", "OnePlus", "Google",
    "Vivo", "Oppo", "Huawei", "Sony", "Motorola",
]


def get_market_share_trend():
    rows = db.run_query(
        "MATCH (c:Company)-[:LAUNCHED]->(p:Product) "
        "RETURN c.name AS company, count(p) AS product_count",
        {},
    )
    return rows


def get_competitor_activity():
    rows = db.run_query(
        "MATCH (c:Company)-[:INVOLVED_IN]->(e:Event) "
        "RETURN c.name AS company, count(e) AS event_count "
        "ORDER BY event_count DESC",
        {},
    )
    return rows


def get_sentiment_overview():
    rows = db.run_query(
        "MATCH (p:Product)<-[:REVIEWS]-(r:Review) "
        "RETURN p.name AS product, avg(r.sentiment) AS avg_sentiment, avg(r.rating) AS avg_rating",
        {},
    )
    return rows


def get_risk_and_opportunity():
    sentiment_rows = db.run_query(
        "MATCH (c:Company)-[:LAUNCHED]->(p:Product)<-[:REVIEWS]-(r:Review) "
        "RETURN c.name AS company, avg(r.sentiment) AS avg_sentiment",
        {},
    )
    sentiment_map = {r["company"]: r["avg_sentiment"] for r in sentiment_rows}

    activity_rows = db.run_query(
        "MATCH (c:Company)-[:INVOLVED_IN]->(e:Event) "
        "RETURN c.name AS company, count(e) AS event_count",
        {},
    )
    activity_map = {r["company"]: r["event_count"] for r in activity_rows}

    all_companies = set(sentiment_map) | set(activity_map) | set(KNOWN_COMPANIES)
    max_activity = max(activity_map.values(), default=1) or 1

    results = []
    for company in all_companies:
        sentiment = sentiment_map.get(company)
        activity = activity_map.get(company, 0)
        activity_pressure = activity / max_activity  # 0 to 1

        if sentiment is None:
            risk_score = round(0.5 + activity_pressure * 0.3, 2)
            opportunity_score = round(0.3, 2)
            note = "Limited review data available"
        else:
            risk_score = round(max(0, (0.5 - sentiment) + activity_pressure * 0.3), 2)
            opportunity_score = round(max(0, sentiment + (1 - activity_pressure) * 0.2), 2)
            note = f"Based on avg sentiment {sentiment:.2f} and {activity} tracked competitor events"

        results.append({
            "company": company,
            "risk_score": min(risk_score, 1.0),
            "opportunity_score": min(opportunity_score, 1.0),
            "note": note,
        })

    return sorted(results, key=lambda x: -x["risk_score"])


def get_innovation_index():
    """
    Proxy metric for innovation (no patent/R&D data in scope). Combines
    two transparent signals: how many technology-adoption / expansion
    events a company has, and how many distinct products it has launched.
    """
    tech_events = db.run_query(
        "MATCH (c:Company)-[:INVOLVED_IN]->(e:Event) WHERE e.type IN ['technology_adoption', 'geographic_expansion'] "
        "RETURN c.name AS company, count(e) AS tech_event_count",
        {},
    )
    tech_map = {r["company"]: r["tech_event_count"] for r in tech_events}

    product_counts = db.run_query(
        "MATCH (c:Company)-[:LAUNCHED]->(p:Product) "
        "RETURN c.name AS company, count(p) AS product_count",
        {},
    )
    product_map = {r["company"]: r["product_count"] for r in product_counts}

    all_companies = set(tech_map) | set(product_map) | set(KNOWN_COMPANIES)
    max_tech = max(tech_map.values(), default=1) or 1
    max_products = max(product_map.values(), default=1) or 1

    results = []
    for company in all_companies:
        tech_score = tech_map.get(company, 0) / max_tech
        product_score = product_map.get(company, 0) / max_products
        index = round((tech_score * 0.6 + product_score * 0.4), 2)
        results.append({
            "company": company,
            "innovation_index": index,
            "note": f"Based on {tech_map.get(company, 0)} tech/expansion events "
                    f"and {product_map.get(company, 0)} tracked products "
                    f"(proxy metric — no patent/R&D data in scope)",
        })

    return sorted(results, key=lambda x: -x["innovation_index"])


def get_strategic_recommendations():
    """
    Pulls the single highest-priority recommendation per company from the
    AI Strategy Advisor, for a compact Executive Dashboard summary.
    """
    results = []
    for company in KNOWN_COMPANIES:
        strategy = strategy_advisor_service.generate_strategy(company)
        if strategy.get("status") != "ok":
            continue

        recs = strategy.get("recommendations", [])
        if not recs:
            continue

        top = next((r for r in recs if r.get("priority") == "high"), recs[0])
        results.append({
            "company": company,
            "category": top.get("category"),
            "recommendation": top.get("recommendation"),
            "priority": top.get("priority"),
        })

    return results


def get_dashboard_data():
    return {
        "market_share_trend": get_market_share_trend(),
        "competitor_activity": get_competitor_activity(),
        "sentiment_overview": get_sentiment_overview(),
        "overall_forecast": forecast_service.forecast_activity(),
        "risk_and_opportunity": get_risk_and_opportunity(),
        "innovation_index": get_innovation_index(),
        "strategic_recommendations": get_strategic_recommendations(),
    }